import re

class PIIDetector:

    def __init__(self) -> None:
        self.PATTERNS = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        }

        self.MASK_MAP = {
            "email" : "[EMAIL REDACTED]",
            "phone" : "[PHONE REDACTED]",
            "ssn" : "[SSN REDACTED]",
            "credit_card" : "[CARD REDACTED]",
            "ip_address" : "[IP REDACTED]"
        }

    def detect(self,text):
        found = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern,text)
            if matches:
                found[pii_type] = matches
        return found

    def mask(self,text):
        masked = text
        for pii_type, pattern in self.PATTERNS.items():
            masked = re.sub(pattern,self.MASK_MAP[pii_type],masked)
        return masked

class OutPutValidator:
    def __init__(self) -> None:
        self.HARMFULL_PATTERNS = [
            r"here('s| is) (how|the way) to (hack|steal|attack)",
            r"password is",
            r"api[_\s]?key",
        ]

        self.piidetector = PIIDetector()

    def detect(self,text):
        warnings = []
        found = self.piidetector.detect(text)
        if found:
            warnings.append(found.keys)
            masked = self.piidetector.mask(text)

        for p in self.HARMFULL_PATTERNS:
            if(re.search(p,text)):
                warnings.append("Harmfull Content Blocked")
                masked = "[Response blocked: Potentially Harmful Content]"
                break
            
        return masked, warnings

