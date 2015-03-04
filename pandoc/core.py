import subprocess
from os.path import exists
from tempfile import NamedTemporaryFile
import os

PANDOC_PATH = 'pandoc'

def set_path(path):
    global PANDOC_PATH
    PANDOC_PATH = path

class Document(object):
    """A formatted document."""
    INPUT_FORMATS = (
        'native', 'markdown', 'rst', 
        'html', 'latex',
    )
    
    # removed pdf and epub which cannot be handled by stdout
    OUTPUT_FORMATS = (
        'native', 'html', 's5', 'slidy', 
        'docbook', 'opendocument', 'odt',
        'latex', 'context', 'texinfo', 
        'man', 'markdown', 'plain', 
        'rst', 'mediawiki', 'rtf', 'markdown_github'
    )

    def __init__(self, arguments=['-s', '--mathjax'], extensions=[]):
        self._content = None
        self._format = None
        self.arguments = arguments
        self.extensions = extensions
        self._register_formats()

    @classmethod
    def _register_formats(cls):
        """Adds format properties."""
        for fmt in cls.OUTPUT_FORMATS:
            setattr(cls, fmt, property(
                (lambda x, fmt=fmt: cls._output(x, fmt)), # fget
                (lambda x, y, fmt=fmt: cls._input(x, y, fmt)))) # fset
    

    def _input(self, value, format=None):
        self._content = value
        self._format = format
        if len(self.extensions) > 0:
            self._format += '+' + '+'.join(self.extensions)
    

    def _output(self, format):
        args = [PANDOC_PATH, '--from=%s' % self._format, '--to=%s' % format]
        args.extend(self.arguments)

        p = subprocess.Popen(
                args,
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE
        )
        return p.communicate(self._content)[0]

    def save(self, output_filename, format=None):
        '''
        Try to save the file to the specified output file.
        Return true if successful
        '''
        args = [PANDOC_PATH, '--from=%s' % self._format, '--output=%s' % output_filename]

        if format != None:
            args.extend(['--to=%s' % format])

        args.extend(self.arguments)      

        p = subprocess.Popen(
                args,
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
        )

        (stdoutdata, stderrdata) = p.communicate(self._content)
        self.pandoc_result = (stdoutdata, stderrdata)
        
        return p.returncode == 0

