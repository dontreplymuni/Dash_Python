import os
import re

print('====== tools ======')

if os.environ.get('environment', '') == 'dash-docs':
    from .server import app
else:
    from server import app, foo
    print(foo)


def exception_handler(func):
    def wrapper(path):
        try:
            return func(path)
        except Exception as e:
            print('\nError running {}\n{}'.format(path, '=' * 76))
            raise e
    return wrapper


@exception_handler
def load_example(path):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), path), 'r') as _f:
        _source = _f.read()
        _example = _source

        # Use the global app assignment
        if 'app = dash.Dash' not in _example and 'app = CustomDash()' not in _example:
            raise Exception("Didn't declare app")
        _example = _example.replace('app = dash.Dash', '# app = dash.Dash')

        commented_configs = [
            'app.scripts.config.serve_locally',
            'app.css.config.serve_locally'
        ]
        for config in commented_configs:
            _example = _example.replace(
                config,
                '# {}'.format(config)
            )

        if 'import dash\n' not in _example:
            raise Exception("Didn't import dash")

        # return the layout instead of assigning it to the global app
        if 'app.layout = ' not in _example:
            raise Exception('app.layout not assigned')
        _example = _example.replace('app.layout = ', 'layout = ')

        # Remove the "# Run the server" commands
        if 'app.run_server' not in _example:
            raise Exception('app.run_server missing')
        _example = _example.replace(
            '\n    app.run_server',
            'print("Running")\n    # app.run_server'
        )

        # if there are lines that should be included in the syntax but
        # not executed, simply put a comment on that line starting "# no-exec"
        # similarly, if there are lines that should be evalued but
        # not executed, simply put a comment on that line starting "# no-display"
        no_exec = '# no-exec'
        no_display = '# no-display'
        if no_exec in _example:
            _example = '\n'.join(
                line for line in _example.splitlines() if no_exec not in line
            )

            find_no_exec = re.compile(r'\s+' + no_exec + '.*')
            _source = '\n'.join(
                find_no_exec.sub('', line) if no_exec in line else line
                for line in _source.splitlines()
            )

        if no_display in _example:
            _source = '\n'.join(
                line for line in _source.splitlines() if no_display not in line
            )

            find_no_display = re.compile(r'\s+' + no_display + '.*')
            _example = '\n'.join(
                find_no_display.sub('', line) if no_display in line else line
                for line in _example.splitlines()
            )

        if '$tools' in _example:
            _example = _example.replace('$tools', os.path.dirname(os.path.realpath(__file__)))

        scope = {'app': app}
        exec(_example, scope)

    return (
        '```python \n' + _source + '```',
        scope['layout']  # layout is a global created from the app
    )


def merge(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def read_file(path):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), path), 'r') as f:
        return f.read()