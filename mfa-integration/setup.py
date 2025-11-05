"""
Setup script for Emotion Auth MFA Python package
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='emotion-auth-mfa',
    version='1.0.0',
    description='Emotion-aware multi-factor authentication backend adapter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Emotion Auth Team',
    author_email='contact@emotion-auth.com',
    url='https://github.com/your-org/emotion-auth-mfa',
    py_modules=['mfa_backend_adapter'],
    install_requires=[
        'requests>=2.25.0',
    ],
    extras_require={
        'flask': ['Flask>=2.0.0'],
        'django': ['Django>=3.2.0'],
        'fastapi': ['fastapi>=0.68.0', 'uvicorn>=0.15.0'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Flask',
        'Framework :: Django',
        'Framework :: FastAPI',
    ],
    python_requires='>=3.7',
    keywords='authentication mfa 2fa biometrics emotion security ai',
    project_urls={
        'Bug Reports': 'https://github.com/your-org/emotion-auth-mfa/issues',
        'Source': 'https://github.com/your-org/emotion-auth-mfa',
        'Documentation': 'https://docs.emotion-auth.com',
    },
)
