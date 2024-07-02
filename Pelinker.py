from os import linesep
import struct
import sys
import time

SECTION_EXECUTABLE = 0x20000020
SECTION_READABLE = 0x40000000
SECTION_WRITABLE = 0x80000000
SECTION_DISCARDABLE = 0x02000000


def align(value, alignment):
    r = value % alignment
    if r > 0:
        return value + (alignment - r)
    return value


def pad(data, size):
    return data.ljust(size, b"\0")


def pad_align(data, alignment):
    return pad(data, align(len(data), alignment))


def le32(*args):
    data = b""
    for arg in args:
        data += struct.pack("<I", arg)
    return data


def le16(*args):
    data = b""
    for arg in args:
        data += struct.pack("<H", arg)
    return data


def le64(*args):
    data = b""
    for arg in args:
        data += struct.pack("<Q", arg)
    return data


def permissions_str(permissions):
    permissions_string = ""
    if permissions & SECTION_READABLE:
        permissions_string += "r"
    if permissions & SECTION_WRITABLE:
        permissions_string += "w"
    if permissions & SECTION_EXECUTABLE:
        permissions_string += "x"
    if permissions & SECTION_DISCARDABLE:
        permissions_string += "d"
    return permissions_string


class Section:
    def __init__(self, name, rva, permissions):
        self.name = name
        self.rva = rva
        self.content = None
        self.relocation_symbols = []
        if isinstance(permissions, str):
            permissions_map = {
                "r": SECTION_READABLE,
                "w": SECTION_WRITABLE,
                "x": SECTION_EXECUTABLE,
                "d": SECTION_DISCARDABLE,
            }
            self.permissions = 0
            for character in permissions.lower():
                if character in permissions_map:
                    self.permissions |= permissions_map[character]
                else:
                    raise Exception("unknown section permissions mask")
        else:
            self.permissions = permissions

    def add_relocation_symbol(self, symbol, offset, relocation_type=4):
        self.relocation_symbols.append((symbol, offset, relocation_type))


class Symbol:
    def __init__(self, name, rva):
        self.name = name
        self.rva = rva


class ImportLibrary:
    def __init__(self, libname, symbols):
        self.libname = libname
        if isinstance(symbols, str):
            raise Exception("ImportLibrary expects an iterable of strings")
        self.symbols = symbols


class Image:
    def __init__(self, image_base, characteristics=0x22):
        self.image_base = image_base
        self.alignment = 0x1000
        self.file_alignment = 0x200
        self.characteristics = characteristics
        self.entry_point = self.alignment
        self.export_table = (0, 0)
        self.import_table = (0, 0)
        self.relocation_table = (0, 0)
        self.sections = []
        self.symbols = []
        self.imports = []
        self.relocations = []

    def get_executable_sections_size(self):
        total = 0
        for section in self.sections:
            if section.content and section.permissions & SECTION_EXECUTABLE:
                total += align(
                    len(section.content)
                    if not isinstance(section.content, int)
                    else section.content,
                    self.alignment,
                )
        return total

    def get_writable_sections_size(self):
        total = 0
        for section in self.sections:
            if section.content and section.permissions & SECTION_WRITABLE:
                total += align(
                    len(section.content)
                    if not isinstance(section.content, int)
                    else section.content,
                    self.alignment,
                )
        return total

    def get_sections_aligned_size(self):
        total = 0
        for section in self.sections:
            if section.content:
                total += align(
                    len(section.content)
                    if not isinstance(section.content, int)
                    else section.content,
                    self.alignment,
                )
        return total

    def get_text_base(self):
        for section in self.sections:
            if section.content and section.permissions & SECTION_EXECUTABLE:
                return section.rva
        return 0

    def _get_next_section_rva(self):
        if self.sections:
            last_section = self.sections[-1]
            if last_section.content:
                return last_section.rva + align(
                    len(last_section.content)
                    if not isinstance(last_section.content, int)
                    else last_section.content,
                    self.alignment,
                )

            return last_section.rva + self.alignment
        return self.alignment

    def add_section(self, name, permissions, content=None):
        rva = self._get_next_section_rva()
        section = Section(name, rva, permissions)
        section.content = content
        self.sections.append(section)
        return section

    def _append_edata_section(self):
        if not self.symbols:
            return

        section = self.add_section(".edata", "r")

        strings_data = b""
        offset = 0
        offsets = []
        for symbol in self.symbols:
            ascii_data = symbol.name.encode("ascii")
            strings_data += ascii_data + b"\0"
            offsets.append(offset)
            offset = len(strings_data)

        strings_base = section.rva + 40 + len(self.symbols) * 10

        section.content = le32(0)
        section.content += le32(int(time.time()))
        section.content += le16(0, 0)
        # points to an empty string
        section.content += le32(strings_base + offset - 1)
        section.content += le32(1)  # Ordinal Base
        section.content += le32(len(self.symbols))
        section.content += le32(len(self.symbols))
        section.content += le32(section.rva + 40)  # Export Address Table RVA
        # Name Pointer RVA
        section.content += le32(section.rva + 40 + len(self.symbols) * 4)
        # Ordinal Table RVA
        section.content += le32(section.rva + 40 + len(self.symbols) * 8)

        for symbol in self.symbols:
            section.content += le32(symbol.rva)

        for index, symbol in enumerate(self.symbols):
            section.content += le32(strings_base + offsets[index])

        for index, symbol in enumerate(self.symbols):
            section.content += le16(index)

        section.content += strings_data

        self.export_table = (
            section.rva,
            len(section.content),
        )

    def _append_idata_section(self):
        if not self.imports:
            return

        section = self.add_section(".idata", "r")

        strings_data = b""
        offset = 0
        offsets = []
        libname_offsets = []
        for libimport in self.imports:
            ascii_data = libimport.libname.encode("ascii")
            strings_data += ascii_data + b"\0"
            libname_offsets.append(offset)
            offset = len(strings_data)
            for symbol in libimport.symbols:
                ascii_data = symbol.encode("ascii") + b"\0"
                additional = b""
                if len(ascii_data) % 2 != 0:
                    additional = b"\0"
                strings_data += le16(0) + ascii_data + additional
                offsets.append(offset)
                offset = len(strings_data)

        section.content = b""

        directory_tables_size = (len(self.imports) + 1) * 20
        import_lookup_tables_size = (
            sum([(len(libimport.symbols) + 1) for libimport in self.imports]) * 8
        )
        import_address_tables_size = import_lookup_tables_size
        strings_data_index = (
            section.rva
            + directory_tables_size
            + import_lookup_tables_size
            + import_address_tables_size
        )

        entries = []
        symbols_counter = 0
        for libimport in self.imports:
            entries.append(symbols_counter)
            symbols_counter += (len(libimport.symbols) + 1) * 8

        for index, libimport in enumerate(self.imports):
            section.content += le32(
                section.rva + directory_tables_size + entries[index]
            )
            section.content += le32(0)
            section.content += le32(0)
            section.content += le32(strings_data_index + libname_offsets[index])
            section.content += le32(
                section.rva
                + directory_tables_size
                + import_lookup_tables_size
                + entries[index]
            )

        # end of import directory table
        section.content += le32(0, 0, 0, 0, 0)

        string_index = 0
        for libimport in self.imports:
            for symbol in libimport.symbols:
                section.content += le64(strings_data_index + offsets[string_index])
                string_index += 1
            section.content += le64(0)

        string_index = 0
        for libimport in self.imports:
            for symbol in libimport.symbols:
                symbol_rva = section.rva + len(section.content)
                print(
                    "Added IAT for {1}@{0} for RVA 0x{2:08X}".format(
                        libimport.libname, symbol, symbol_rva
                    )
                )
                self._patch_symbol(
                    symbol, symbol_rva, "{0}@{1}".format(symbol, libimport.libname)
                )
                section.content += le64(strings_data_index + offsets[string_index])
                string_index += 1
            section.content += le64(0)

        section.content += strings_data

        self.import_table = (
            section.rva,
            len(section.content),
        )

    def _patch_symbol(self, symbol_name, symbol_rva, symbol_full_name=None):
        for user_section in self.sections:
            self._patch_section_symbol(
                user_section, symbol_name, symbol_rva, symbol_full_name
            )

    def _patch_section_symbol(
        self, section, symbol_name, symbol_rva, symbol_full_name=None
    ):
        if symbol_full_name is None:
            symbol_full_name = symbol_name

        if not section.content:
            return
        for (
            relocation_symbol,
            relocation_offset,
            relocation_type,
        ) in section.relocation_symbols:
            if relocation_symbol == symbol_name:
                struct_format = "<I"
                struct_size = 4
                if relocation_type == 4:
                    relative_relocation = (
                        symbol_rva - (section.rva + relocation_offset) - 4
                    )
                elif relocation_type == 2:
                    relative_relocation = self.image_base + symbol_rva
                elif relocation_type == 1:
                    relative_relocation = self.image_base + symbol_rva
                    struct_format = "<Q"
                    struct_size = 8
                elif relocation_type == 0:
                    continue
                else:
                    raise Exception(
                        "Unsupported relocation type {0} for {1}".format(
                            hex(relocation_type), symbol_full_name
                        )
                    )
                user_section_content = bytearray(section.content)
                original_value = struct.unpack(
                    struct_format,
                    user_section_content[
                        relocation_offset : relocation_offset + struct_size
                    ],
                )[0]
                user_section_content[
                    relocation_offset : relocation_offset + struct_size
                ] = struct.pack(struct_format, relative_relocation + original_value)
                section.content = user_section_content
                print(
                    "Patched RVA 0x{0:08X} with {1} from 0x{2:016X} to 0x{3:016X}".format(
                        section.rva + relocation_offset,
                        symbol_full_name,
                        original_value,
                        relative_relocation,
                    )
                )

    def _append_reloc_section(self):
        if not self.relocations:
            return

        section = self.add_section(".reloc", "rd")

        # build the pages list
        pages = {}
        for relocation in self.relocations:
            page = relocation & 0xFFFFFFFFFFF000
            offset = relocation & 0xFFF
            if not page in pages:
                pages[page] = []
            pages[page].append(offset)

        section.content = b""

        sorted_pages = sorted(pages.keys())

        for sorted_page in sorted_pages:
            offsets = pages[sorted_page]
            block = b""
            for offset in offsets:
                block += le16(offset | 0x0A << 12)
            section.content += le32(sorted_page & 0xFFFFFFFF)
            section.content += le32(len(block) + 8)
            section.content += block

        self.relocation_table = (section.rva, len(section.content))

    def export_symbol(self, name, rva):
        symbol = Symbol(name, rva)
        self.symbols.append(symbol)
        return symbol

    def import_symbols(self, libname, symbols):
        importlib = ImportLibrary(libname, symbols)
        self.imports.append(importlib)
        return importlib

    def link(self):
        # append .edata section
        if self.symbols:
            self._append_edata_section()

        # append .idata section
        if self.imports:
            self._append_idata_section()

        # append .reloc section
        if self.relocations:
            self._append_reloc_section()

        dos_header = bytearray(b"MZ" + b"\0" * 62)
        dos_header[0x3C] = 0x40  # offset of the pe_header

        pe_header = b"PE\0\0"
        pe_header += le16(0x8664)  # Machine
        pe_header += le16(len(self.sections))
        pe_header += le32(int(time.time()))  # TimeDateStamp
        pe_header += le32(0, 0)  # PointerToSymbolTable, NumberOfSymbols
        pe_header += le16(0xF0)  # SizeOfOptionalHeader
        pe_header += le16(self.characteristics)  # Characteristics

        optional_header = le16(0x020B)  # Magic
        optional_header += b"\x01\x01"
        optional_header += le32(self.get_executable_sections_size())
        # SizeOfInitializedData
        optional_header += le32(self.get_writable_sections_size())
        optional_header += le32(0)  # SizeOfUninitializedData
        optional_header += le32(self.entry_point)
        optional_header += le32(self.get_text_base())

        optional_header += le64(self.image_base)
        optional_header += le32(self.alignment)
        optional_header += le32(self.file_alignment)
        # MajorOperatingSystemVersion, MinorOperatingSystemVersion
        optional_header += le16(6, 0)
        # MajorImageVersion, MinorImageVersion
        optional_header += le16(0, 0)
        # MajorSubsystemVersion , MinorSubsystemVersion
        optional_header += le16(6, 0)
        optional_header += le32(0)  # Win32VersionValue

        headers_size = align(
            len(dos_header) + len(pe_header) + 0xF0 + (len(self.sections) * 40),
            self.file_alignment,
        )
        headers_size_in_image = align(
            len(dos_header) + len(pe_header) + 0xF0 + (len(self.sections) * 40),
            self.alignment,
        )

        # SizeOfImage
        optional_header += le32(
            headers_size_in_image + self.get_sections_aligned_size()
        )

        optional_header += le32(headers_size)  # SizeOfHeaders

        optional_header += le32(0)  # CheckSum
        optional_header += le16(3)  # Subsystem
        optional_header += le16(
            0x8100 | 0x60 if self.relocations else 0
        )  # DllCharacteristics
        optional_header += le64(0x10000)  # SizeOfStackReserve
        optional_header += le64(0x10000)  # SizeOfStackCommit
        optional_header += le64(0x10000)  # SizeOfHeapReserve
        optional_header += le64(0x10000)  # SizeOfHeapCommit
        optional_header += le32(0)  # LoaderFlags
        optional_header += le32(0x10)  # NumberOfRvaAndSizes

        optional_header += le32(*self.export_table)  # Export Table
        optional_header += le32(*self.import_table)  # Import Table
        optional_header += le32(0, 0)  # Resource Table
        optional_header += le32(0, 0)  # Exception Table
        optional_header += le32(0, 0)  # Certificate Table
        optional_header += le32(*self.relocation_table)  # Base Relocation Table
        optional_header += le32(0, 0)  # Debug
        optional_header += le32(0, 0)  # Architecture
        optional_header += le32(0, 0)  # Global Ptr
        optional_header += le32(0, 0)  # TLS Table
        optional_header += le32(0, 0)  # Local Config Table
        optional_header += le32(0, 0)  # Bound Import
        optional_header += le32(0, 0)  # IAT
        optional_header += le32(0, 0)  # Delay Import
        optional_header += le32(0, 0)  # CLR
        optional_header += le32(0, 0)  # Reserved

        sections_header = b""
        data_offset = headers_size

        for section in self.sections:
            self._patch_symbol(section.name, section.rva)

        for section in self.sections:
            ascii_name = section.name.encode("ascii")
            if len(ascii_name) > 8:
                raise Exception("invalid section name size")
            section_size = 0
            section_file_size = 0
            if section.content:
                if isinstance(section.content, int):
                    section_size = section.content
                    section.permissions |= 0x80
                else:
                    section_size = len(section.content)
                    section_file_size = section_size
                if not section.permissions & 0x20 and not section.permissions & 0x80:
                    section.permissions |= 0x40
            sections_header += pad(ascii_name, 8)
            sections_header += le32(align(section_size, self.alignment))
            sections_header += le32(section.rva)
            sections_header += le32(align(section_file_size, self.file_alignment))
            sections_header += le32(data_offset)
            sections_header += le32(0)  # PointerToRelocations
            sections_header += le32(0)  # PointerToLinenumbers
            sections_header += le16(0)  # NumberOfRelocations
            sections_header += le16(0)  # NumberOfLinenumbers
            sections_header += le32(section.permissions)  # Characteristics

            print(
                "Added section {0} at RVA 0x{1:08X} permissions {2}".format(
                    section.name, section.rva, permissions_str(section.permissions)
                )
            )

            data_offset += align(section_file_size, self.file_alignment)

        blob = pad_align(
            dos_header + pe_header + optional_header + sections_header,
            self.file_alignment,
        )

        for section in self.sections:
            if section.content:
                if not isinstance(section.content, int):
                    blob += pad_align(section.content, self.file_alignment)

        print(
            "Successfully linked at base 0x{0:016X} (entry point at RVA 0x{1:08X})".format(
                self.image_base, self.entry_point
            )
        )

        return blob


class Executable(Image):
    def __init__(self, image_base=0x00400000):
        super().__init__(image_base)

    def add_relocation(self, rva):
        self.relocations.append(rva)


class SharedLibrary(Image):
    def __init__(self, image_base=0x10000000):
        super().__init__(image_base, 0x2022)
        self.entry_point = 0


class COFF:
    def __init__(self, data):
        (
            self.machine,
            self.number_of_sections,
            self.time_date_stamp,
            self.pointer_to_symbol_table,
            self.number_of_symbols,
            self.size_of_optional_header,
            self.characteristics,
        ) = struct.unpack("<HHIIIHH", data[0:20])
        self.sections = []

        string_table_offset = self.pointer_to_symbol_table + (
            self.number_of_symbols * 18
        )

        offset = 20
        for _ in range(0, self.number_of_sections):
            (
                name,
                _,
                _,
                size_of_raw_data,
                pointer_to_raw_data,
                pointer_to_relocations,
                _,
                number_of_relocations,
                _,
                characteristics,
            ) = struct.unpack("<8sIIIIIIHHI", data[offset : offset + 40])

            new_section_name = name.rstrip(b"\0").decode()
            new_section_permissions = permissions_str(characteristics)

            if pointer_to_raw_data > 0:
                new_section_data = (
                    data[pointer_to_raw_data : pointer_to_raw_data + size_of_raw_data]
                    if pointer_to_raw_data
                    else b""
                )
            else:
                # uninitialized data?
                new_section_data = size_of_raw_data
            new_section_relocation_symbols = []
            for relocation_index in range(0, number_of_relocations):
                relocation = data[
                    pointer_to_relocations
                    + (relocation_index * 10) : pointer_to_relocations
                    + ((relocation_index + 1) * 10)
                ]
                (
                    relocation_symbol_address,
                    relocation_symbol_index,
                    relocation_symbol_type,
                ) = struct.unpack("<IIH", relocation)
                relocation_symbol_offset = self.pointer_to_symbol_table + (
                    relocation_symbol_index * 18
                )
                (
                    symbol_name,
                    symbol_value,
                    _,
                    _,
                    _,
                    _,
                ) = struct.unpack(
                    "<8sIHHBB",
                    data[relocation_symbol_offset : relocation_symbol_offset + 18],
                )

                if symbol_name[0:4] == b"\0\0\0\0":
                    symbol_name = (
                        data[
                            string_table_offset
                            + struct.unpack("<I", symbol_name[4:8])[0] :
                        ]
                        .split(b"\0")[0]
                        .decode()
                    )
                else:
                    symbol_name = symbol_name.rstrip(b"\0").decode()

                new_section_relocation_symbols.append(
                    (
                        symbol_name,
                        relocation_symbol_address,
                        relocation_symbol_type,
                    )
                )

            self.sections.append(
                (
                    new_section_name,
                    new_section_permissions,
                    new_section_data,
                    new_section_relocation_symbols,
                )
            )
            offset += 40


if __name__ == "__main__":
    exe = Executable()

    text = exe.add_section(".text", "rx")
    text.content = open(sys.argv[1], "rb").read()

    exe.entry_point = text.rva

    open(sys.argv[2], "wb").write(exe.link())