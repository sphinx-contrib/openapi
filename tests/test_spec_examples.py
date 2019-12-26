"""Smoke test examples from OAI/OpenAPI-Specification repo."""

import os
import glob
import itertools

import py
import pytest


@pytest.mark.parametrize('spec', itertools.chain(
    glob.glob(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'OpenAPI-Specification',
            'examples',
            'v2.0',
            'json',
            '*.json')),

    glob.glob(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'OpenAPI-Specification',
            'examples',
            'v2.0',
            'yaml',
            '*.yaml')),
))
def test_openapi2_success(tmpdir, run_sphinx, spec):
    py.path.local(spec).copy(tmpdir.join('src', 'test-spec.yml'))
    run_sphinx('test-spec.yml')


@pytest.mark.parametrize('group_paths', [False, True])
@pytest.mark.parametrize('render_examples', [False, True])
@pytest.mark.parametrize('render_request', [False, True])
@pytest.mark.parametrize('spec', glob.glob(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'OpenAPI-Specification',
        'examples',
        'v3.0',
        '*.yaml')
))
def test_openapi3_success(tmpdir, run_sphinx, spec, render_examples,
                          render_request, group_paths):
    py.path.local(spec).copy(tmpdir.join('src', 'test-spec.yml'))
    run_sphinx('test-spec.yml', options={
        'examples': render_examples,
        'request': render_request,
        'group': group_paths,
    })
