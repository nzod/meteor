#encoding: UTF-8

'''
module:   sx
version:  0.9

The venerable sx module.
Getting long overdue treatment.

CHANGES:
TODO:

'''

def replacei(s, i, s2):
   return '%s%s%s' % (s[:i], s2, s[i+1:])

def replace_multi(s, with_dict):
   ret = s
   for k,v in with_dict.iteritems():
      ret = ret.replace(k, v)
   return ret

def unchar(s, char=' '):
   ret = []
   is_prev = False
   for c in s:
      if c == char:
         if is_prev: continue
         else:
            is_prev = True
      else:
         is_prev = False
      ret.append(c)
   return ''.join(ret)

def unwhite(s):
   return unchar(s.strip())

def map_clean(li):
   return [unwhite(s) for s in li if s.strip()]

def prepend(pre, s):
   return (s if s.startswith(pre) else pre+s)

def append(post, s):
   return (s if s.endswith(post) else s+post)

def lshave(pre, s):
   return (s[len(pre):] if s.startswith(pre) else s)

def rshave(post, s):
   return (s[:-(len(post))] if s.endswith(post) else s)

def keep_chars(s, chars):
   return ''.join([c for c in s if c in chars])

def remove_chars(s, chars):
   return ''.join([c for c in s if not (c in chars)]) 

#def strip_char(s, char):
#   while s.startswith(char):
#      s = s[1:]
#   while s.endswith(char):
#      s = s[:-1]
#   return s

def has_any(s, stuff):
   for x in stuff:
      if x in s:
         return True
   return False
   
def strip_left_any(s, chars):
   origlen = len(s)
   if origlen==1 and (not s in chars):
      return s
   ret = []
   slen = origlen
   starti = 0
   while True:
      if slen==0:
         return ''
      if s[starti] in chars:
         slen -= 1
         starti += 1
      else:
         break
   return s[starti:]

def strip_any(s, chars):
   origlen = len(s)
   if origlen==1 and (not s in chars):
      return s
   ret = []
   slen = origlen
   starti = 0
   while True:
      if slen==0:
         return ''
      if s[starti] in chars:
         slen -= 1
         starti += 1
      else:
         break
   endi = origlen-1
   while True:
      if endi==0:
         return ''
      if s[endi] in chars:
         endi -= 1
      else:
         break
   return s[starti:endi+1]

def split_any(s, chars):
   ret = []
   splits = []
   currword = []
   for c in s:
      if c in chars:
         ret.append(''.join(currword))
         currword=[]
         splits.append(c)
      else:
         currword.append(c)
   ret.append(''.join(currword))
   return ret, splits
   
def join_any(li, splits):
   ret = [li[0], ]
   for i,sp in enumerate(splits):
      ret.append(sp)
      ret.append(li[i+1])
   return ''.join(ret)
   
def starts_any(s, ses):
   if not ses:
      return False
   for test in ses:
      if s.startswith(test):
         return True
   return False
   
def ends_any(s, ses):
   if not ses:
      return False
   for test in ses:
      if s.endswith(test):
         return True
   return False
   
   
