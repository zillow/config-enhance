# Copyright (c) 2012 Zillow
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
from ConfigParser import ConfigParser as CP

__ALL__ = ["enhance_platform_versions", "enhance"]

LOG = logging.getLogger (__name__)

class EnhanceSection(object):
    '''Enhance a section based on the content of a << item
    
    operators are
    <[sectionname] - bring in values that don't already exist in the section
    +[sectionname] - bring in all values, overwriting any current content
    -[sectionname] - remove values that exist in the named section

    The enhancements are executed in order, which only matters if you use
    the removal operator. Then order can impact the behavior of a following
    '<'.
    '''

    def __init__ (self, config, name):
        self.config = config
        self.name = name
        self.ops = []
        self._extract_ops ()

    @property
    def is_complete(self):
        return len(self.ops) == 0

    def __call__ (self):
        '''Apply all the enhancements to the current section.'''
        for op_type, from_section in self.ops:
            if op_type == '<':
                self._enhance_with_base (from_section)
            elif op_type == '+':
                self._enhance_with_mixin (from_section)
            elif op_type == '-':
                self._enhance_with_removal (from_section)
        self.ops = []

    def _enhance_with_base (self, from_section):
        for k, v in self.config.items (from_section):
            if not self.config.has_option (self.name, k):
                self.config.set (self.name, k, v)

    def _enhance_with_mixin (self, from_section):
        for k, v in self.config.items (from_section):
            self.config.set (self.name, k, v)

    def _enhance_with_removal (self, from_section):
        for k, v in self.config.items (from_section):
            self.config.remove_option (self.name, k)

    def _extract_ops (self):
        op_key = '<<'
        simple_op_key = '<'

        if self.config.has_option (self.name, op_key):
            # get the operation items from the << = entry.
            #  '<foo +bar -baz <biz'
            op_item = self.config.get (self.name, op_key)
            self.config.remove_option(self.name, op_key)
            self.ops = parse_ops_from_config_item (op_item)

        if self.config.has_option(self.name, simple_op_key):
            value = self.config.get(self.name, simple_op_key)
            value = value.strip ()
            self.ops.insert (0, ('<', value))

def parse_ops_from_config_item (value):
    '''Parse the <<= config item for enhancements.'''
    values = [vv for vv in value.split () if vv]
    
    ops = []
    
    next_is_section = False
    last_op = None

    for vv in values:
        if next_is_section:
            # second token for '+ sectionname'
            ops.append ((last_op, vv))
            next_is_section = False
            last_op = None
        elif len(vv) == 1:
            # first token for '+ sectionname'
            last_op = vv
            next_is_section = True
        elif len(vv) > 1:
            # like +sectionname, the op and name are merged in one string
            op, section = vv[0], vv[1:]
            ops.append ((vv[0], vv[1:]))
    return ops



class Target(object):
    '''A target that needs to be built.

    Maintains a list of required inputs, impacted dependants, and the action
    to perform when the required inputs are complete.

    @reqs - the targets needed to build this target
    @deps - dependants that need this
    @action - action to perfom to build this target

    The action must be callable with no parameters. It must implement
    "is_complete", which should return true when the target that will
    result from the action is complete.

    The action may just deteect that no action is needed and mark itself
    as complete.
    '''
    def __init__ (self, action):
        self.action = action
        self.reqs = set()
        self.deps = set()
        self._reqs_complete = False

    @property
    def reqs_complete (self):
        if self._reqs_complete:
            return True

        for req in self.reqs:
            if not req.is_complete:
                return False
        
        self._reqs_complete = True
        return self._reqs_complete
    
    def __call__ (self):
        '''Build the target by executing the action.'''
        self.action()

    @property
    def is_complete (self):
        return self.action.is_complete


def build_targets (targets):
    '''Build a list of targets.
    
    @targets - collection of targets to build

    Returns the targets that couldn't be built due to unmet requirements.
    '''
    seeds = [tgt for tgt in targets if tgt.reqs_complete]
    built = set()
    
    progress_made = True
    while len(seeds) and progress_made:
        new_seeds = set()
        for target in seeds:
            target()
            built.add(target)
            new_seeds.update(target.deps)
        seeds = [seed for seed in new_seeds if seed.reqs_complete]
    
    unbuilt = set(targets).difference(built)
    return unbuilt


def enhance_platform_versions (cp):
    section_meta = {}
    simple_op_key = '<'
    op_key = '<<'

    has_error = False

    # define a work target for every section in the config file
    for section in cp.sections():
        action = EnhanceSection(cp, section)
        target = Target(action)
        section_meta[section] = target
    
    # figure out the target dependencies
    for meta in section_meta.itervalues():
        for op_type, op_section in meta.action.ops:
            try:
                other_meta = section_meta[op_section]
            except KeyError, ke:
                LOG.error("section '%s' requires '%s', but '%s' does not exist", section, op_section, op_section)
                has_error = True
            else:
                other_meta.deps.add(meta)
                meta.reqs.add(other_meta)
        
    unbuilt = build_targets (section_meta.values())



enhance = enhance_platform_versions

