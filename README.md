# config-enhance

config-enhance adds re-use capabilities to ConfigParser style config files.

It introduces a reserved key: '<<='

The '<<=' key should be assigned a list of enhancements like:

    [section]
    <<=
        <other1
        +other2
        <other3
        -other4

Each enhancement is composed of an operator followed by a section name. The operators are:

- '<' : mix things in from another section if they don't already exist
- '+' : pull config from another section, overwrite settings in the current section
       if there is a clash.
- '-' : remove config items that exist in the source section from this section

You can use it like this:

    from config_enhance import enhance
    
    cp = ConfigParser (file ("my.cfg"))
    enhance(cp)

Suppose that my.cfg contains content like:

    [common]
    flup = 1.0
    requests = 2.0
    
    [tes_100]
    <<= <common
    requests = 5.0
    tornado = 6.0
    
    [dev_tes_common]
    tornado = 6.0d
    
    [dev_unpin]
    flup = unpin
    
    [dev_tes_100]
    <<=
        <tes_100
        +dev_tes_common
        -dev_unpin

After running enhance, 'cp' will be modified to contain:

    [common]
    flup = 1.0
    requests = 2.0
    
    [tes_100]
    flup = 1.0
    requests = 5.0
    tornado = 6.0
    
    [dev_tes_common]
    tornado = 6.0d
    
    [dev_unpin]
    flup = unpin
    
    [dev_tes_100]
    requests = 5.0
    tornado = 6.0d


# target audience

config-enhance is useful when managing version requirement sections in buildout.
Buildout already contains limited reuse features through the '<=' idiom. But,
version management is easier with an extended set.

## Other docs of interest

[config parser documentation](http://docs.python.org/2/library/configparser.html)

