%Generating the profile for an optimal taper
%Created by Di Zhu on Jul 31, 2017
%Update:
%- fixed error of 2pi in the bending section
%- modified for CPW transmission lines (20171103)
%- for microstrip, simply ignore the gap size (set to any value), then use
%[x2,y2] and [x3, y3] as the outline
%- Corrected a crucial error on the direction of l, i.e., section length
%problem (Apr 2018)
%-20180906 reduce number of sections in the taper.
%-20190815 corrected the missing factor of A/2pi for the total length
%-revised by Marco Colangelo Nov 2019 to remove pigtails
clear;
close all;
saveflag = 1;

load('erickson_nbn.mat')

bending_radius_factor = 3; %normally I use 3
gap = 12; %gap size for cpw
w1 = 1;
lmax = 2500; %maximum length for each turn (this is for bending the taper)
Zo=50;      % Characteristic impedance to match to (Ohms)
Fo= 500;    % Lower cut-off frequency (MHz)
F1=50;       % Start frequency for response plot (MHz)
F2=20000;   % Stop frequency for response plot (MHz)
%Tlen=0.0001;  % Transformer length as a fraction of wavelength

f = Fo*1e6; %design frequency 
lmd0 = 3e8/f; %design free space wavelength
%dlmd0 = Tlen*lmd0;

total_length = erickson_l;

N = 6000;
dlmd0 = total_length/N; %length per section
Tlen = dlmd0/lmd0; %section length in terms of wavelength

disp('caculating optimal taper');
figure
%This generate a taper from 50 ohm to high impedance
Zlist = erickson_Z;

% Return loss and smith chart plots
bplot(Zlist,Tlen,Fo,F1,F2);
Zsim

%find the widths for each transformer section
Wlist = interp1(Zsim, wsim, Zlist,'pchip');
%this is to get rid of the problem that the last section somehow suddenly
%getts narrower
if Wlist(1)< Wlist(2)
    Wlist(1) = Wlist(2);
end
nlist = interp1(Zsim, sqrt(epssim), Zlist,'pchip');

%I prefer to start from the narrow end
%This should be done before calculation of l
nlist = fliplr(nlist);
Wlist = fliplr(Wlist);
Zlist = fliplr(Zlist);

%length and section cut for the entire taper
l(1) = 0;
for i = 2:length(nlist)
    l(i) = l(i-1)+dlmd0/nlist(i-1);
end

dlmd0= dlmd0*1e6; %convert into micron

l = l*1e6; %in micron

%calculate total number of squares
num_of_squares = sum(dlmd0./(nlist.*Wlist))


% 
figure
plot(l, Wlist,'*-');
xlabel('length');
ylabel('width');



%generate coordinate for the boundary for GDS file

%all tracking indices
row = 1;
x0 = zeros(size(l));x0=x0';
y0 = x0;
x1 = x0; y1 = x0; x2 = x0; y2 = y0; x3 = x0; y3 = x0; x4 = x0; y4 = x0;
y1(1) = Wlist(1)/2+gap;
y2(1) = Wlist(1)/2;
y3(1) = -Wlist(1)/2;
y4(1) = -Wlist(1)/2-gap;
i = 2;
ltrack = 0;
flag_finish_before_turn=0;
cut_point = [];

M=360;%number of points while turning
disp('start generating gds coordinates');
fprintf('%d,',i);
Wlist=Wlist(1:end-1);
nlist=nlist(1:end-1);
l=l(1:end-1);
while ltrack < max(l)
    if mod(i,5000)==0
        fprintf('%d,',i);
    end
    if mod(row,2) == 1
        w = interp1(l, Wlist, ltrack,'pchip'); 
        if (w+2*gap) < 25
            r0 = bending_radius_factor*(w+2*gap); %radius of curvature to the width 
        else
            r0 = 3*(w+2*gap); %radius of curvature to the width
            if r0 < bending_radius_factor*25
                r0 = bending_radius_factor*25;
            end
        end
        
        disp(r0)
        
        if r0 + x0(i-1) < lmax/2 
            %straight, to the right
            dl = dlmd0/interp1(Wlist, nlist, w,'pchip');
            x0(i) = x0(i-1)+dl;
            y0(i) = y0(i-1);
            x1(i) = x0(i); y1(i) = y0(i)+w/2+gap;
            x2(i) = x0(i); y2(i) = y0(i)+w/2;
            x3(i) = x0(i); y3(i) = y0(i)-w/2;
            x4(i) = x0(i); y4(i) = y0(i)-w/2-gap;
            i = i+1;
            ltrack = ltrack+dl;
        else
            %start to turn, clockwise
            disp('turn')
            Ox0 = x0(i-1);
            Oy0 = y0(i-1)-r0;
            theta = [0:pi/M:pi];
            for jj = 2:length(theta)
                if ltrack>=l
                    w = Wlist(end);
                else
                    w = interp1(l, Wlist, ltrack,'pchip');
                end
                x0(i) = Ox0+r0*sin(theta(jj));
                y0(i) = Oy0+r0*cos(theta(jj));
                x1(i) = Ox0+(r0+w/2+gap)*sin(theta(jj));
                y1(i) = Oy0+(r0+w/2+gap)*cos(theta(jj));
                x2(i) = Ox0+(r0+w/2)*sin(theta(jj));
                y2(i) = Oy0+(r0+w/2)*cos(theta(jj));
                x3(i) = Ox0+(r0-w/2)*sin(theta(jj));
                y3(i) = Oy0+(r0-w/2)*cos(theta(jj));
                x4(i) = Ox0+(r0-w/2-gap)*sin(theta(jj));
                y4(i) = Oy0+(r0-w/2-gap)*cos(theta(jj));
                i = i+1;
                ltrack=ltrack+r0*pi/M;
                if ltrack > max(l) %fished while turning
                    %keep turn until its
                    flag_finish_before_turn=1;
                end  
            end
            if flag_finish_before_turn
                fprintf('\n finished while turning')
            end
            row = row+1;
        end
    else
        w = interp1(l, Wlist, ltrack,'pchip'); 
        if (w+2*gap) < 25
            r0 = bending_radius_factor*(w+2*gap); %radius of curvature to the width 
        else
            r0 = 1.5*(w+2*gap); %reduce the radius of curvature for wide wires
            if r0 < bending_radius_factor*25
                r0 = bending_radius_factor*25;
            end
        end
        if  x0(i-1)-r0 > -lmax/2 
            %straight, to the left
            dl = dlmd0/interp1(Wlist, nlist, w,'pchip');
            x0(i) = x0(i-1)-dl;
            y0(i) = y0(i-1);
            x1(i) = x0(i); y1(i) = y0(i)-w/2-gap;
            x2(i) = x0(i); y2(i) = y0(i)-w/2;
            x3(i) = x0(i); y3(i) = y0(i)+w/2;
            x4(i) = x0(i); y4(i) = y0(i)+w/2+gap;
            i = i+1;
            ltrack=ltrack+dl;
        else
            %start to turn, counter-clockwise
            Ox0 = x0(i-1);
            Oy0 = y0(i-1)-r0;
            theta = [0:pi/M:pi];
            for jj = 2:length(theta)
                if ltrack>=l
                    w = Wlist(end);
                else
                    w = interp1(l, Wlist, ltrack,'pchip');
                end
                x0(i) = Ox0-r0*sin(theta(jj));
                y0(i) = Oy0+r0*cos(theta(jj));
                x4(i) = Ox0-(r0+w/2+gap)*sin(theta(jj));
                y4(i) = Oy0+(r0+w/2+gap)*cos(theta(jj));
                x3(i) = Ox0-(r0+w/2)*sin(theta(jj));    
                y3(i) = Oy0+(r0+w/2)*cos(theta(jj));
                x2(i) = Ox0-(r0-w/2)*sin(theta(jj));    
                y2(i) = Oy0+(r0-w/2)*cos(theta(jj));
                x1(i) = Ox0-(r0-w/2-gap)*sin(theta(jj));
                y1(i) = Oy0+(r0-w/2-gap)*cos(theta(jj));
                
                i = i+1;
                ltrack=ltrack+r0*pi/M;
                if ltrack > max(l) %fished while turning
                    %keep turn until its
                    flag_finish_before_turn=1;
                end 
            end
            if flag_finish_before_turn
                fprintf('\n finished while turning')
            end
            row=row+1;
        end
    end
    
end
fprintf('%d\n', i);

disp('ltrack')
disp(ltrack)

%add pigtails to the top
buffer = 10;
theta = [0:pi/M:pi/2-pi/M];theta = theta';
w = y2(1)-y3(1);
r0 = 3*(w+2*gap);
pts_x0 = -r0*cos(theta);
pts_y0 = r0-r0*sin(theta);
pts_x1 = -(r0-w/2-gap)*cos(theta);
pts_y1 = r0-(r0-w/2-gap)*sin(theta);
pts_x2 = -(r0-w/2)*cos(theta);
pts_y2 = r0-(r0-w/2)*sin(theta);
pts_x3 = -(r0+w/2)*cos(theta);
pts_y3 = r0-(r0+w/2)*sin(theta);
pts_x4 = -(r0+w/2+gap)*cos(theta);
pts_y4 = r0-(r0+w/2+gap)*sin(theta);
x0 = [pts_x0(1);pts_x0; x0];
y0 = [pts_y0(1)+buffer;pts_y0; y0];
x1 = [pts_x1(1);pts_x1; x1];
y1 = [pts_y1(1)+buffer;pts_y1; y1];
x2 = [pts_x2(1);pts_x2; x2];
y2 = [pts_y2(1)+buffer;pts_y2; y2];
x3 = [pts_x3(1);pts_x3; x3];
y3 = [pts_y3(1)+buffer;pts_y3; y3];
x4 = [pts_x4(1);pts_x4; x4];
y4 = [pts_y4(1)+buffer;pts_y4; y4];


%% fix the bug
i2 = find(x0, 1, 'last')
x0=x0(1:i2);
y0=y0(1:i2);
x1=x1(1:i2);
y1=y1(1:i2);
x2=x2(1:i2);
y2=y2(1:i2);
x3=x3(1:i2);
y3=y3(1:i2);
x4=x4(1:i2);
y4=y4(1:i2);


%add pigtails on the bot
buffer = 10;

if mod(row, 2) ==1
    theta = [pi/M:pi/M:pi/2];theta = theta';
    w = y2(end)-y3(end);
    r0 = 3*(w+2*gap);
    pts_x0 = x0(end)+r0*sin(theta);
    pts_y0 = y0(end)-r0+r0*cos(theta);
    pts_x4 = x0(end)+(r0-w/2-gap)*sin(theta);
    pts_y4 = y0(end)-r0+(r0-w/2-gap)*cos(theta);
    pts_x3 = x0(end)+(r0-w/2)*sin(theta);
    pts_y3 = y0(end)-r0+(r0-w/2)*cos(theta);
    pts_x2 = x0(end)+(r0+w/2)*sin(theta);
    pts_y2 = y0(end)-r0+(r0+w/2)*cos(theta);
    pts_x1 = x0(end)+(r0+w/2+gap)*sin(theta);
    pts_y1 = y0(end)-r0+(r0+w/2+gap)*cos(theta);

else
    theta = [pi/M:pi/M:pi/2];theta = theta';
    w = abs(y2(end)-y3(end));
    r0 = 3*(w+2*gap);
    pts_x0 = x0(end)-r0*sin(theta);
    pts_y0 = y0(end)-r0+r0*cos(theta);
    pts_x1 = x0(end)-(r0-w/2-gap)*sin(theta);
    pts_y1 = y0(end)-r0+(r0-w/2-gap)*cos(theta);
    pts_x2 = x0(end)-(r0-w/2)*sin(theta);
    pts_y2 = y0(end)-r0+(r0-w/2)*cos(theta);
    pts_x3 = x0(end)-(r0+w/2)*sin(theta);
    pts_y3 = y0(end)-r0+(r0+w/2)*cos(theta);
    pts_x4 = x0(end)-(r0+w/2+gap)*sin(theta);
    pts_y4 = y0(end)-r0+(r0+w/2+gap)*cos(theta);
end
x0 = [x0; pts_x0; pts_x0(end)];
y0 = [y0; pts_y0; pts_y0(end)-buffer];
x1 = [x1; pts_x1; pts_x1(end)];
y1 = [y1; pts_y1; pts_y1(end)-buffer];
x2 = [x2; pts_x2; pts_x2(end)];
y2 = [y2; pts_y2; pts_y2(end)-buffer];
x3 = [x3; pts_x3; pts_x3(end)];
y3 = [y3; pts_y3; pts_y3(end)-buffer];
x4 = [x4; pts_x4; pts_x4(end)];
y4 = [y4; pts_y4; pts_y4(end)-buffer];



figure(4)
plot(x0/1e3,y0/1e3, 'k-.')
axis equal;
hold on
plot(x1/1e3, y1/1e3,'k-', x2/1e3, y2/1e3,'k-', x3/1e3, y3/1e3,'k-', x4/1e3, y4/1e3,'k-');
%plot(x1,y1,'k-'); plot(x2,y2,'k-');
xlabel('x (mm)'); ylabel('y (mm)')
