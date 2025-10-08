import hashlib, hmac, sys, os
key = os.environ.get('RULES_SIGNING_KEY','dev-key-change').encode()
p = sys.argv[1] if len(sys.argv)>1 else 'rules.yml'
b = open(p,'rb').read().rstrip(b'\n')
sig = hmac.new(key, b, hashlib.sha256).hexdigest()
open(p,'wb').write(b + b'\n# sig=' + sig.encode() + b'\n')
print(sig)
