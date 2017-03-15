class PrinterWrapper(object):
    def __init__(self):
        self.printer = None
    def add_printer(self, printer):
        print ("adding printer", printer)
        response = True
        return response
    def remove_printer(self, printer):
        print ("removing printer", printer)
        response = True
        return response
    def list_printers(self):
        print ("listing printers")
        data = []
        data.append("HP")
        data.append("Lexmark")
        return data