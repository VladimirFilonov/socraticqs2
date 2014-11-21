from django.utils.safestring import mark_safe
#from markdown import markdown
from django import template
import re
import pypandoc
from django.contrib.staticfiles.templatetags import staticfiles
from django.utils import timezone
from datetime import timedelta

register = template.Library()

InlineMathPat = re.compile(r'\\\((.+?)\\\)', flags=re.DOTALL)
DisplayMathPat = re.compile(r'\\\[(.+?)\\\]', flags=re.DOTALL)
StaticImagePat = re.compile(r'STATICIMAGE/([^"]+)')

@register.filter(name='md2html')
def md2html(txt, stripP=False):
    'converst ReST to HTML using pandoc, w/ audio support'
    txt, markers = add_temporary_markers(txt, find_audio)
    txt, videoMarkers = add_temporary_markers(txt, find_video, len(markers))
    txt = pypandoc.convert(txt, 'html', format='rst',
                           extra_args=('--mathjax',))
    txt = replace_temporary_markers(txt, audio_html, markers)
    txt = replace_temporary_markers(txt, video_html, videoMarkers)
    txt = StaticImagePat.sub(staticfiles.static('ct/') + r'\1', txt)
    if stripP and txt.startswith('<p>') and txt.endswith('</p>'):
        txt = txt[3:-4]
    return mark_safe(txt)

def nolongerused():
    'convert markdown to html, preserving latex delimiters'
    # markdown replaces \( with (, so have to protect our math...
    # replace \(math\) with \\(math\\)
    txt = InlineMathPat.sub(r'\\\\(\1\\\\)', txt)
    # replace \[math\] with \\[math\\]
    txt = DisplayMathPat.sub(r'\\\\[\1\\\\]', txt)
    txt = markdown(txt, safe_mode='escape')
    if stripP and txt.startswith('<p>') and txt.endswith('</p>'):
        txt = txt[3:-4]
    return mark_safe(txt)

def find_audio(txt, lastpos, tag='.. audio::'):
        i = txt.find(tag, lastpos)
        if i < 0:
            return -1, None, None
        lastpos = i + len(tag)
        k = txt.find('\n', lastpos)
        if k < 0:
            k = txt.find('\r', lastpos)
        if k < 0: # no EOL, slurp to end of text
            k = len(txt)
        v = txt[lastpos:k].strip()
        return i, k, v

def find_video(txt, lastpos, tag='.. video::'):
    return find_audio(txt, lastpos, tag)

def audio_html(filename):
    i = filename.rfind('.')
    if i > 0: # remove file suffix
        filename = filename[:i]
    return '<audio controls><source src="STATICIMAGE/%s.ogg" type="audio/ogg"><source src="STATICIMAGE/%s.mp3" type="audio/mpeg">no support for audio!</audio>' \
      % (filename,filename)
    
def video_html(filename):
    try:
        sourceDB, sourceID = filename.split(':')
    except ValueError:
        return 'ERROR: bad video source: %s' % filename
    d = {
        'youtube': '''<iframe width="560" height="315"
        src="http://www.youtube.com/embed/%s?rel=0"
        frameborder="0" allowfullscreen></iframe>
        ''',
        'vimeo': '''<iframe width="500" height="281"
        src="http://player.vimeo.com/video/%s"
        frameborder="0" webkitallowfullscreen mozallowfullscreen
        allowfullscreen></iframe>
        ''',
        }
    try:
        return d[sourceDB] % sourceID
    except KeyError:
        return 'ERROR: unknown video sourceDB: %s' % sourceDB

def add_temporary_markers(txt, func, base=0, l=None):
    s = ''
    lastpos = 0
    if l is None:
        l = []
    while True: # replace selected content with unique markers
        i, j, v = func(txt, lastpos)
        if i < 0: # no more markers
            break
        marker = 'mArKeR:%d:' % (base + len(l))
        l.append((marker, v))
        s += txt[lastpos:i] + marker
        lastpos = j
    s += txt[lastpos:]
    return s, l

def replace_temporary_markers(txt, func, l):
    s = ''
    lastpos = 0
    for marker, v in l: # put them back in after conversion
        i = txt.find(marker, lastpos)
        if i < 0:
            continue # must have been removed by comment, so ignore
        s += txt[lastpos:i] + func(v)  # substitute value
        lastpos = i + len(marker)
    s += txt[lastpos:]
    return s

def get_base_url(path, extension=[], baseToken='units', tail=2):
    l = path.split('/')
    for i,v in enumerate(l):
        if v == baseToken:
            return '/'.join(l[:i + tail] + extension) + '/'
    raise ValueError('baseToken not found in path')

def get_path_type(path, baseToken='units', typeOffset=2):
    l = path.split('/')
    for i, s in enumerate(l[:-typeOffset]):
        if s == baseToken:
            return l[i + typeOffset]
    raise ValueError('baseToken not found in path')


def is_teacher_url(path):
    return path.startswith('/ct/teach/')

@register.filter(name='get_object_url')
def get_object_url(actionTarget, o, forceDefault=False, subpath=None):
    basePath = get_base_url(actionTarget)
    try:
        urlFunc = o.get_url
    except AttributeError:
        if subpath:
            tail = subpath + '/'
        elif subpath is None:
            tail = 'teach/'
        else:
            tail = ''
        head = getattr(o, '_headURL', o.__class__.__name__.lower())
        return  '%s%s/%d/%s' % (basePath, head, o.pk,
                                getattr(o, '_subURL', tail))
    else:
        return urlFunc(basePath, forceDefault, subpath,
                       is_teacher_url(basePath))
    
@register.filter(name='get_forced_url')
def get_forced_url(actionTarget, o, subpath=None):
    return get_object_url(actionTarget, o, True, subpath)

@register.filter(name='get_thread_url')
def get_thread_url(actionTarget, r):
    'get URL for FAQ thread for this student inquiry'
    return get_object_url(actionTarget, r.unitLesson,
                          subpath='faq/%d' % r.pk)

##############################################################
# time utilities

timeUnits = (('seconds', timedelta(minutes=1), lambda t:int(t.seconds)),
             ('minutes', timedelta(hours=1), lambda t:int(t.seconds / 60)),
             ('hours', timedelta(1), lambda t:int(t.seconds / 3600)),
             ('days', timedelta(7), lambda t:t.days))

monthStrings = ('Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.',
                'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.')

@register.filter(name='display_datetime')
def display_datetime(dt):
    'get string that sidesteps timezone issues thus: 27 minutes ago'
    def singularize(i, s):
        if i == 1:
            return s[:-1]
        return s
    diff = timezone.now() - dt
    for unit, td, f in timeUnits:
        if diff < td:
            n = f(diff)
            return '%d %s ago' % (n, singularize(n, unit))
    return '%s %d, %d' % (monthStrings[dt.month - 1], dt.day, dt.year)


