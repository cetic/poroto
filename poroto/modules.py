import config

class Template:
    def __init__(self, name, debug):
        self.name = name
        self.debug = debug
        self.export = False
        self.inline = False
        self.nb_instances = 0

    def instanciate(self, instance_name, from_instance):
        raise Exception("Method not implemented")

    def instanciate_inline(self, call_node):
        pass

    def add_instance_ref(self, instance_name, from_name):
        self.nb_instances += 1

    def check_usage(self, ref_count):
        pass

class Instance:
    def __init__(self, debug):
        self.debug = debug
        self.name=None
        self.args=None
        self.decl=None
        self.system = False
        self.from_instance=None
        self.streams = []
        self.params = {}
        self.streams_map = {}

    def generate(self, designer):
        pass
 
    def update_code(self):
        pass
    
    def instanciate_streams(self, streams_map):
        if self.name in streams_map.blocks:
            for stream in streams_map.blocks[self.name].itervalues():
                self.add_stream(stream)

    def add_stream(self, stream):
        if self.debug: print "Add stream %s to %s" % (stream.name, self.name)
        self.streams.append(stream)
        self.streams_map[stream.name] = stream
        stream.assign_instance(self, self.from_instance)
        
    def resolve_streams(self, mems_map):
        if len(self.streams) > 0:
            print "Resolving streams for %s" % self.name
        for stream in self.streams:
            stream.resolve_stream(mems_map)

    def validate(self):
        pass

class FunctionsRegistry():
    def __init__(self, designer, mems_map, debug):
        self.debug = debug
        self.designer = designer
        self.mems_map = mems_map
        self.streams_map = None
        self.functions = []

        self.function_templates = {}
        self.function_usages = {}
        self.function_refs = {}
        self.function_count = {}
        self.function_instances_id = {}
        self.instances_list = []
        self.depth = 0

    def addTemplateToRegistry(self, template):
        if self.debug: print "Register template %s" % template.name
        self.function_templates[template.name] = template
        if not template.name in self.function_refs:
            self.function_refs[template.name] = []
            self.function_count[template.name] = 0

    def get_template(self, template_name):
        if template_name in self.function_templates:
            template=self.function_templates[template_name]
            return template
        else:
            raise Exception("Function template '%s' not found" % template_name)

    def instanciate(self, template_name, instance_name, from_instance):
        template = self.get_template(template_name)
        if self.debug: print "Instanciating %s %s as %s" % (template.__class__.__name__, template_name, instance_name)
        function = template.instanciate(instance_name, from_instance)
        function.instanciate_streams(self.streams_map)
        return function

    def add_instance_ref(self, template_name, instance_name, from_instance):
        template = self.get_template(template_name)
        template.add_instance_ref(instance_name, from_instance)

    def resolveInstanceSubtree(self, function_name, instance):
        if not function_name in self.function_usages: return
        self.depth+=1
        for callee in self.function_usages[function_name]:
            print "%s Resolve sub tree for %s from %s" % ("**" * self.depth, callee, function_name)
            if config.duplicate_functions:
                if not callee in self.function_instances_id:
                    self.function_instances_id[callee] = 0
                callee_instance_id = self.function_instances_id[callee] + 1
                self.function_instances_id[callee] = callee_instance_id
                if callee_instance_id != 1:
                    callee_instance_name = callee + '_' + str(callee_instance_id)
                else:
                    callee_instance_name = callee
                callee_instance = self.instanciate(callee, callee_instance_name, instance)
                self.resolveInstanceSubtree(callee, callee_instance)
                callee_instance.update_code()
                self.instances_list.append(callee_instance)
            else:
                callee_instance_name = callee
                if not callee in self.function_instances_id:
                    self.function_instances_id[callee] = 0
                    callee_instance = self.instanciate(callee, callee_instance_name, instance)
                    self.resolveInstanceSubtree(callee, callee_instance)
                    callee_instance.update_code()
                    self.instances_list.append(callee_instance)
        self.depth-=1

    def resolveInstanceTree(self):
        for name, ref in self.function_refs.iteritems():
            if self.debug: print "ResolveInstanceTree: %s" % name
            template=self.function_templates[name]
            if len(ref) == 0 and not template.inline:
                print "Resolve tree for %s" % name
                instance = self.instanciate(name, name, None)
                self.resolveInstanceSubtree(name, instance)
                self.instances_list.append(instance)
                if template.export:
                    self.functions.append(instance)

    def checkUsage(self):
        for (template_name, count) in self.function_count.iteritems():
            template = self.get_template(template_name)
            if self.debug: print "Usage of %s : %d" % (template_name, count)
            template.check_usage(count)

    def consolidate(self):
        self.resolveInstanceTree()
        self.checkUsage()
        for instance in self.instances_list:
            instance.resolve_streams(self.mems_map)
        for instance in self.instances_list:
            instance.generate(self.designer)
        for instance in self.instances_list:
            instance.validate()

    def register_manual_reference(self, function_name, call_name):
        if self.debug: print "Registering dependency %s -> %s" % (function_name, call_name)
        if not call_name in self.function_refs:
            self.function_refs[call_name] = []
            self.function_count[call_name] = 0
        if not function_name in self.function_refs[call_name]:
            self.function_refs[call_name].append(function_name)
        self.function_count[call_name] += 1

        if not function_name in self.function_usages:
            self.function_usages[function_name] = []
        if not call_name in self.function_usages[function_name]:
            self.function_usages[function_name].append(call_name)

    def register_reference(self, current_function, call_name):
        self.register_manual_reference(current_function, call_name)

    def clone_reference(self, current_function, inline_name):
        if inline_name in self.function_usages:
            for callee_name in self.function_usages[inline_name]:
                self.register_reference(current_function, callee_name)
