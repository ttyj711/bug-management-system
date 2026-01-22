#!/usr/bin/env python
"""
JWT兼容性补丁
修复djangorestframework-simplejwt 4.4.0与PyJWT 2.x的兼容性问题
"""

import jwt
from django.utils.translation import ugettext_lazy as _
from jwt import InvalidTokenError

from rest_framework_simplejwt.backends import TokenBackend as OriginalTokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError

# 保存原始的encode方法
original_encode = OriginalTokenBackend.encode

def patched_encode(self, payload):
    """
    修复后的encode方法
    处理PyJWT 2.x返回字符串而不是字节对象的情况
    """
    jwt_payload = payload.copy()
    if self.audience is not None:
        jwt_payload['aud'] = self.audience
    if self.issuer is not None:
        jwt_payload['iss'] = self.issuer

    token = jwt.encode(jwt_payload, self.signing_key, algorithm=self.algorithm)
    # PyJWT 2.x返回字符串，不需要decode
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token

# 应用补丁
def apply_jwt_patch():
    """应用JWT补丁"""
    OriginalTokenBackend.encode = patched_encode
    print("JWT补丁已应用")
