import sys
import traceback


def print_error_explanation(message):
    lines = message.strip().split("\n")
    max_len = max([len(x) for x in lines])

    print('=' * max_len, file=sys.stderr)
    for line in lines:
        print(line, file=sys.stderr)
    print('=' * max_len, file=sys.stderr)
    
def display(e: Exception, task):
    print(f"{task or 'error'}: {type(e).__name__}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

    
already_displayed = {}    
    
def display_once(e: Exception, task):
    if task in already_displayed:
        return

    display(e, task)

    already_displayed[task] = 1


def run(code, task):
    try:
        code()
    except Exception as e:
        display(task, e)