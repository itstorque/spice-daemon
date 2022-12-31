import spice_daemon as sd

File = sd.helpers.file_interface.File

f = File("./test2/testCreate.asc")

print(f)

print(f.read())