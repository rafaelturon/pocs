class PrinterWrapper(object):
    def __init__(self):
        self.printer = None
    def add_printer(self, params):
        print ("adding printer url", params['printerUrl'])
        print ("adding install url", params['installUrl'])
        response = True
        return response
    def remove_printer(self, params):
        print ("removing printer url", params['printerUrl'])
        print ("removing install url", params['installUrl'])
        response = True
        return response
    def list_printers(self):
        print ("listing printers")
        data = []
        data.append("HP")
        data.append("Lexmark")
        return data