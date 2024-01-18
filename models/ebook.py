import os
import xml.etree.ElementTree as ET
import tiktoken


def require_open_context(method):
    def wrapper(self, *args, **kwargs):
        if not self._is_open:
            raise Exception("Ebook must be opened with 'with' statement")
        return method(self, *args, **kwargs)
    return wrapper


class Ebook:
    file_type = ".txt" 

    def __init__(self, file_path: str):
        if not self.is_correct_type(file_path):
            raise Exception(f"The file '{file_path}' not found or it is not '{self.file_type}' file")
        self._file_path = file_path
        self._file = None
        self._is_open = False

    def is_correct_type(self, _file_path):
        if not os.path.isfile(_file_path):
            return False
        
        _, file_extension = os.path.splitext(_file_path)
        return file_extension.lower() == self.file_type.lower()

    def open_ebook(self):
        try:
            self._file = open(self._file_path, 'r')
            self._is_open = True
        except Exception as e:
            print(f"Failed to open the ebook: {e}")
            raise
        return self
    
    def close_ebook(self):
        self._file.close()
        self._is_open = False

    def __enter__(self):
        return self.open_ebook()

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            try:
                self.close_ebook()
            except Exception as e:
                print(f"Failed to close the ebook: {e}")
                raise
        if exc_type is not None:
            print(f"An exception occurred: {exc_type}, {exc_value}")
            return False
    
    @require_open_context
    def get_raw(self):
        if not self._file:
            raise Exception("Could not read the file, it is not found")
        return self._file.read()

    @require_open_context
    def get_text(self):
        return self.get_raw()


class Fb2(Ebook):
    file_type = ".fb2"

    def __init__(self, _file_path: str):
        super().__init__(_file_path)
        self.ns = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'}
        self._tree = None
        self._root = None
    
    def open_ebook(self):
        self._tree = ET.parse(self._file_path)
        self._root = self._tree.getroot()
        self._is_open = True
        return self
    
    def close_ebook(self):
        self._tree = None
        self._root = None
        self._is_open = False
    
    @require_open_context
    def get_text(self):
        try:
            # Find all <p> elements and concatenate their text content
            text_elements = self._root.findall('.//fb:p', self.ns)
            text = "\n".join(elem.text for elem in text_elements if elem.text)
            return text
        except ET.ParseError as e:
            raise Exception(f"XML Parsing Error: {e}")
    
    @require_open_context
    def get_raw(self):
        return ET.tostring(self._root, encoding='unicode')


# Example usage
try:
    with Ebook('temp.txt') as ebook:
        print(ebook.get_raw())
except Exception as e:
    print(f"Error occurred: {e}")