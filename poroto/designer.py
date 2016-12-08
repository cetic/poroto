class Designer:
    def __init__(self):
        self.files = []
        self.filesmap = {}

    def add_file(self, category, filename, synth=True, sim=True):
        if filename not in self.filesmap:
            file={'cat': category, 'file': filename, 'synth': synth, 'sim': sim}
            self.files.append(file)
            self.filesmap[filename] = file

    def generate(self, project_path):
        raise Exception("Method not implemented")
