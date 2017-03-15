from printer_wrapper import PrinterWrapper

printer = PrinterWrapper()
printer.add_printer('Lexmark')
printer.remove_printer('HP')
printer.list_printers()