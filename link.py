from Pelinker import Executable, COFF
import sys
import os

assembler = "C:/Program Files/NASM/nasm.exe"

coffs = []

for asm_source_file in sys.argv[1:-1]:  #gli OBJ file sono tutti quei file arricchiti che contengono altre gli opcode anche tutte le informazioni sui simboli, mapapture di memoria, ecc.. 
    asm_object_file = "{0}.o".format(asm_source_file)

    os.system(
        '"{0}" -f win64 -o {1} {2}'.format(assembler, asm_object_file, asm_source_file)
    )

    with open(asm_object_file, "rb") as handle:
        coffs.append(COFF(handle.read()))

exe = Executable()
exe.minimal_import = True
exe.use_plt = True  # Procedure Linkage Table
exe.join_sections = True

for coff in coffs:
    for (
        section_name,
        section_permissions,
        section_data,
        relocations,
        symbols,
    ) in coff.sections:
        new_section = exe.add_section(section_name, section_permissions, section_data)
        for reloc_name, reloc_offset, reloc_type in relocations:
            new_section.add_relocation_symbol(reloc_name, reloc_offset, reloc_type)
        for known_symbol in symbols:
            new_section.add_symbol(known_symbol, symbols[known_symbol])
            exe.export_symbol(known_symbol, exe.get_symbol_rva(known_symbol))

exe.import_symbols("user32.dll")

exe.entry_point = exe.get_symbol_rva("start")

with open(sys.argv[-1], "wb") as handle:
    handle.write(exe.link())
