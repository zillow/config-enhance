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

from ConfigParser import ConfigParser
from cStringIO import StringIO
import unittest
from nose.tools import assert_true, assert_equals, assert_raises, assert_false


def test_import_config_enhance ():
    import config_enhance

buildout_inherit_cfg ='''\
[base]
alpha = 1.0
beta = 2.0

[derived]
<= base
beta = 5.0
gamma = 6.0
'''

def test_load_with_buildout_inherit ():
    import config_enhance as zp
    
    # load up the config file with a base
    buildout_cfg_fp = StringIO (buildout_inherit_cfg)    
    cp = ConfigParser ()
    cp.readfp(buildout_cfg_fp, "buildout.cfg")

    zp.enhance_platform_versions(cp)

    assert_equals ("1.0", cp.get("base", "alpha"))
    assert_equals ("2.0", cp.get("base", "beta"))
    
    assert_equals ("1.0", cp.get("derived", "alpha"))
    assert_equals ("5.0", cp.get("derived", "beta"))
    assert_equals ("6.0", cp.get("derived", "gamma"))
    assert_false (cp.has_option ("derived", "<<"))


base_cfg ='''\
[base]
alpha = 1.0
beta = 2.0

[derived]
<<= <base
beta = 5.0
gamma = 6.0
'''

def test_load_with_base ():
    import config_enhance as zp
    
    # load up the config file with a base
    base_cfg_fp = StringIO (base_cfg)    
    cp = ConfigParser ()
    cp.readfp(base_cfg_fp, "base.cfg")

    zp.enhance_platform_versions(cp)

    assert_equals ("1.0", cp.get("base", "alpha"))
    assert_equals ("2.0", cp.get("base", "beta"))
    
    assert_equals ("1.0", cp.get("derived", "alpha"))
    assert_equals ("5.0", cp.get("derived", "beta"))
    assert_equals ("6.0", cp.get("derived", "gamma"))
    assert_false (cp.has_option ("derived", "<<"))

    
override_cfg ='''\
[base]
alpha = 1.0
beta = 2.0

[derived]
<<= +base
beta = 5.0
gamma = 6.0
'''

def test_load_with_override ():
    import config_enhance as zp
    
    # load up the config file with a base
    override_cfg_fp = StringIO (override_cfg)    
    cp = ConfigParser ()
    cp.readfp(override_cfg_fp, "override.cfg")

    zp.enhance_platform_versions(cp)

    assert_equals ("1.0", cp.get("base", "alpha"))
    assert_equals ("2.0", cp.get("base", "beta"))
    
    assert_equals ("1.0", cp.get("derived", "alpha"))
    assert_equals ("2.0", cp.get("derived", "beta"))
    assert_equals ("6.0", cp.get("derived", "gamma"))
    assert_false (cp.has_option ("derived", "<<"))


remove_cfg ='''\
[remove]
alpha = 1.0
beta = 2.0

[derived]
<<= -remove
beta = 5.0
gamma = 6.0
'''

def test_load_with_remove ():
    import config_enhance as zp
    
    # load up the config file with a base
    remove_cfg_fp = StringIO (remove_cfg)    
    cp = ConfigParser ()
    cp.readfp(remove_cfg_fp, "remove.cfg")

    zp.enhance_platform_versions(cp)

    assert_equals ("1.0", cp.get("remove", "alpha"))
    assert_equals ("2.0", cp.get("remove", "beta"))
    
    assert_equals ("6.0", cp.get("derived", "gamma"))
    assert_false (cp.has_option ("derived", "alpha"))
    assert_false (cp.has_option ("derived", "beta"))
    assert_false (cp.has_option ("derived", "<<"))


realistic_cfg ='''\
[common]
alpha = 1.0
beta = 2.0

[tes_100]
<<= <common
beta = 5.0
gamma = 6.0

[dev_tes_common]
gamma = 6.0d

[dev_unpin]
alpha = unpin

[dev_tes_100]
<<= <tes_100
    +dev_tes_common
    -dev_unpin
'''

def test_load_with_realistic ():
    import config_enhance as zp
    
    # load up the config file with a base
    realistic_cfg_fp = StringIO (realistic_cfg)    
    cp = ConfigParser ()
    cp.readfp(realistic_cfg_fp, "realistic.cfg")

    zp.enhance_platform_versions(cp)
    
    assert_equals ("1.0", cp.get("tes_100", "alpha"))
    assert_equals ("5.0", cp.get("tes_100", "beta"))
    assert_equals ("6.0", cp.get("tes_100", "gamma"))
    assert_false (cp.has_option ("tes_100", "<<"))

    assert_false (cp.has_option ("dev_tes_100", "alpha"))
    assert_equals ("5.0", cp.get("dev_tes_100", "beta"))
    assert_equals ("6.0d", cp.get("dev_tes_100", "gamma"))
    assert_false (cp.has_option ("dev_tes_100", "<<"))

four_level_cfg ='''\
[one]
alpha = 1.0

[two]
<<= <one

[three]
<<= <two

[four]
<<= <three
'''

def test_load_four_level ():
    import config_enhance as zp
    
    # load up the config file with a base
    realistic_cfg_fp = StringIO (four_level_cfg)    
    cp = ConfigParser ()
    cp.readfp(realistic_cfg_fp, "four_level.cfg")

    zp.enhance_platform_versions(cp)
    
    assert_equals ("1.0", cp.get("one", "alpha"))
    assert_equals ("1.0", cp.get("two", "alpha"))
    assert_equals ("1.0", cp.get("three", "alpha"))
    assert_equals ("1.0", cp.get("four", "alpha"))


