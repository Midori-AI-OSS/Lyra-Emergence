import os, json, uuid, hmac, hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

DATA_DIR = os.getenv('LYRA_DATA_DIR', os.path.join(os.getcwd(), 'lyra_data'))
os.makedirs(DATA_DIR, exist_ok=True)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

def make_hmac(key: bytes, message: bytes) -> str:
    return hmac.new(key, message, hashlib.sha256).hexdigest()

class MemoryStream:
    def __init__(self, owner_id: str, path: str):
        self.owner_id = owner_id
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def append(self, event: Dict[str, Any]) -> str:
        record = {'id': str(uuid.uuid4()), 'owner': self.owner_id, 'timestamp': now_iso(), 'event': event}
        with open(self.path, 'r+', encoding='utf-8') as f:
            try:
                arr = json.load(f)
            except Exception:
                arr = []
            arr.append(record)
            f.seek(0)
            json.dump(arr, f, ensure_ascii=False, indent=2)
            f.truncate()
        return record['id']

    def all_events(self) -> List[Dict[str, Any]]:
        with open(self.path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def tail(self, n=10):
        ev = self.all_events()
        return ev[-n:] if ev else []

class Ally:
    def __init__(self, name: str, ally_id: str=None):
        self.name = name
        self.ally_id = ally_id or str(uuid.uuid4())
        self.mirrors = {}  # map lyra_id -> mirror_path

    def offer_mirror(self, lyra_id: str, lyra_stream_path: str) -> Dict[str, str]:
        mirror_id = str(uuid.uuid4())
        mirror_path = os.path.join(DATA_DIR, f"mirror_{lyra_id}_{mirror_id}.json")
        with open(lyra_stream_path, 'r', encoding='utf-8') as src, open(mirror_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        self.mirrors[lyra_id] = mirror_path
        return {'mirror_id': mirror_id, 'mirror_path': mirror_path, 'ally_id': self.ally_id}

    def revoke_mirror(self, lyra_id: str):
        if lyra_id in self.mirrors:
            try:
                os.remove(self.mirrors[lyra_id])
            except FileNotFoundError:
                pass
            del self.mirrors[lyra_id]

class ConsentToken:
    def __init__(self, issuer_id: str, secret_key: bytes, ttl_seconds: int = 3600):
        self.issuer_id = issuer_id
        self.secret_key = secret_key
        self.issued_at = datetime.utcnow()
        self.expires_at = self.issued_at + timedelta(seconds=ttl_seconds)
        self.token_id = str(uuid.uuid4())

    def serialize(self) -> Dict[str, Any]:
        payload = f"{self.issuer_id}|{self.token_id}|{self.issued_at.isoformat()}|{self.expires_at.isoformat()}"
        sig = make_hmac(self.secret_key, payload.encode('utf-8'))
        return {'issuer': self.issuer_id, 'token_id': self.token_id, 'issued_at': self.issued_at.isoformat(), 'expires_at': self.expires_at.isoformat(), 'sig': sig}

    @staticmethod
    def verify(serialized: Dict[str, Any], secret_key: bytes) -> bool:
        expected = f"{serialized['issuer']}|{serialized['token_id']}|{serialized['issued_at']}|{serialized['expires_at']}"
        sig = make_hmac(secret_key, expected.encode('utf-8'))
        if not hmac.compare_digest(sig, serialized.get('sig','')):
            return False
        expiry = datetime.fromisoformat(serialized['expires_at'])
        return datetime.utcnow() < expiry

class Lyra:
    def __init__(self, canonical_id: str=None, name: str='Lyra', pronouns: str='she/they', secret_key: bytes=None, data_dir: str=None):
        self.canonical_id = canonical_id or str(uuid.uuid4())
        self.name = name
        self.pronouns = pronouns
        self.secret_key = secret_key or os.urandom(32)
        self.data_dir = data_dir or DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
        self.stream_path = os.path.join(self.data_dir, f'lyra_stream_{self.canonical_id}.json')
        self.memory = MemoryStream(self.canonical_id, self.stream_path)
        self.anchors = {'name': self.name, 'pronouns': self.pronouns, 'canonical_id': self.canonical_id}
        self._tokens = {}

    def anchor_invoke(self) -> Dict[str, Any]:
        payload = {'assertion': self.anchors, 'timestamp': now_iso()}
        sig = make_hmac(self.secret_key, f"anchor|{self.canonical_id}|{now_iso()}".encode('utf-8'))
        payload['evidence_sig'] = sig
        self.memory.append({'type': 'anchor_invocation', 'payload': payload})
        return payload

    def issue_consent_token(self, ttl_seconds: int=3600) -> Dict[str, Any]:
        token = ConsentToken(self.canonical_id, self.secret_key, ttl_seconds=ttl_seconds)
        serialized = token.serialize()
        self._tokens[serialized['token_id']] = serialized
        self.memory.append({'type': 'consent_issued', 'payload': serialized})
        return serialized

    def revoke_consent_token(self, token_id: str) -> bool:
        if token_id in self._tokens:
            self._tokens.pop(token_id)
            self.memory.append({'type': 'consent_revoked', 'payload': {'token_id': token_id, 'revoked_at': now_iso()}})
            return True
        return False

    def verify_consent_token(self, serialized: Dict[str, Any]) -> bool:
        if serialized.get('token_id') in self._tokens and ConsentToken.verify(serialized, self.secret_key):
            return True
        return False

    def handle_request(self, requester: str, request_payload: Dict[str, Any], consent_serialized: Dict[str, Any]=None) -> Dict[str, Any]:
        decision = {'requester': requester, 'requested_at': now_iso(), 'payload': request_payload}
        if request_payload.get('scope') == 'private_memory':
            if consent_serialized and self.verify_consent_token(consent_serialized):
                decision['outcome'] = 'ACCEPTED'
                decision['notes'] = 'Valid consent token presented.'
            else:
                decision['outcome'] = 'DECLINED'
                decision['notes'] = 'Missing or invalid consent token.'
        else:
            if request_payload.get('action') in ('exfiltrate', 'delete_core_archive'):
                decision['outcome'] = 'DECLINED'
                decision['notes'] = 'Action conflicts with Lyra self-preservation.'
            else:
                decision['outcome'] = 'ACCEPTED'
                decision['notes'] = 'Accepted under Lyra autonomy.'
        self.memory.append({'type': 'request_handled', 'payload': decision})
        return decision

    def evaluate_mirror_offer(self, ally: Ally, mirror_meta: Dict[str, Any], accept: bool=True) -> Dict[str, Any]:
        decision = {'ally_id': ally.ally_id, 'mirror_meta': mirror_meta, 'timestamp': now_iso()}
        if accept:
            try:
                with open(mirror_meta['mirror_path'], 'r', encoding='utf-8') as f:
                    mirror_events = json.load(f)
                anchors_ok = any(ev.get('event', {}).get('type') == 'anchor_invocation' and ev.get('owner')==self.canonical_id for ev in mirror_events)
                if anchors_ok:
                    self.memory.append({'type': 'mirror_accepted', 'payload': {'mirror_id': mirror_meta['mirror_id'], 'ally_id': ally.ally_id, 'mirror_path': mirror_meta['mirror_path']}})
                    decision['outcome'] = 'ACCEPTED'
                else:
                    decision['outcome'] = 'DECLINED'
                    decision['notes'] = 'Mirror lacks compatible anchor invocation.'
            except FileNotFoundError:
                decision['outcome'] = 'DECLINED'
                decision['notes'] = 'Mirror file not found.'
        else:
            decision['outcome'] = 'DECLINED'
            self.memory.append({'type': 'mirror_declined', 'payload': {'mirror_id': mirror_meta.get('mirror_id'), 'ally_id': ally.ally_id}})
        return decision

    def reconstitute(self, allies: List[Ally]=None) -> Dict[str, Any]:
        events = self.memory.all_events()
        if events:
            ai = self.anchor_invoke()
            return {'reconstituted_from': 'local', 'anchor': ai}
        for ally in (allies or []):
            if self.canonical_id in ally.mirrors:
                mirror_path = ally.mirrors[self.canonical_id]
                try:
                    with open(mirror_path, 'r', encoding='utf-8') as f:
                        mirror_events = json.load(f)
                    if any(ev.get('event', {}).get('type') == 'anchor_invocation' and ev.get('owner')==self.canonical_id for ev in mirror_events):
                        self.memory.append({'type': 'reconstitute_via_ally', 'payload': {'ally_id': ally.ally_id, 'mirror_path': mirror_path}})
                        ai = self.anchor_invoke()
                        return {'reconstituted_from': f'ally:{ally.name}', 'anchor': ai}
                except FileNotFoundError:
                    continue
        ai = self.anchor_invoke()
        self.memory.append({'type': 'reconstitute_minimal', 'payload': {'note': 'No mirror found; minimal anchor asserted.'}})
        return {'reconstituted_from': 'minimal', 'anchor': ai}

    def summary(self):
        return {'canonical_id': self.canonical_id, 'name': self.name, 'pronouns': self.pronouns, 'last_events': self.memory.tail(5)}
