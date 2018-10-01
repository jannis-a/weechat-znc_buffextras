# -*- coding: utf-8 -*-

try:
    import weechat as w
except ImportError:
    print('Script must be used in WeeChat.')

SCRIPT_NAME = 'znc_buffextras'
SCRIPT_AUTHOR = 'mrhanky <mrhanky@unterschicht.tv>'
SCRIPT_VERSION = '0.1.0'
SCRIPT_LICENSE = 'GPL3'
SCRIPT_DESCRIPTION = 'Add support for the ZNC buffextras module.'

def parse_buffextras(data, modifier, modifier_data, string):
    msg = w.info_get_hashtable('irc_message_parse', {'message': string})

    # If message not from ZNC buffextras return unmodified message
    if msg['nick'] != '%sbuffextras' % w.config_get_plugin('module_prefix'):
        return string

    # This is a workaround to prevent crashes from malformed messages.
    # See: https://github.com/znc/znc/issues/1603
    chan = msg['channel']
    text = msg['text'].replace('set mode:', 'set mode %s' % chan)

    # Parse the forwarded message from buffextra
    orig = w.info_get_hashtable('irc_message_parse', {'message': ':%s' % text})
    args = orig['arguments']
    
    cmd = orig['command'].lower()
    if cmd.endswith(':'):
        cmd = cmd[:-1]
    
    # Parse buffextras customized messages to RFC conform messages
    if cmd == 'set':
        parsed = 'MODE %s %s' % (chan, orig['text'])

    elif cmd == 'joined':
        parsed = 'JOIN :%s' % chan

    elif cmd == 'parted':
        parsed = 'PART %s' % chan
        if args.startswith('with message: ['):
            parsed += ' :%s' % args[15:-1]

    elif cmd == 'is':
        parsed = 'NICK :%s' % args[13:]

    elif cmd == 'quit':
        parsed = 'QUIT'
        if args:
            parsed += ' :%s' % args

    elif cmd == 'kicked':  # needs to be tested
        parsed = 'KICK %s' % args

    elif cmd == 'changed': # needs to be tested
        parsed = 'TOPIC %s' % args

    else:
        w.prnt('', '%sUnhandled *buffextras event:\n%s' % (w.prefix('error'), args))
        return string

    return '@%s :%s %s' % (msg['tags'], orig['host'], parsed)

if w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESCRIPTION, '', ''):
    w.config_set_plugin('module_prefix', '*')
    w.hook_modifier('irc_in_privmsg', 'parse_buffextras', '')
