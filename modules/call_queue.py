import sys
import threading
import traceback
import time

queue_lock = threading.Lock()


def wrap_queued_call(func):
    def f(*args, **kwargs):
        with queue_lock:
            res = func(*args, **kwargs)
        return res
    return f

def wrap_gradio_gpu_call(func, extra_outputs=None):
    
    def f(*args, **kwargs):
        
        with queue_lock:
            ##TODO: 增加GPU计算的处理逻辑
            try:
                res = func(*args, **kwargs)
            except:
                ...
        return res 
    return wrap_gradio_call(f, extra_outputs, add_stats=True)

def wrap_gradio_call(func, extra_outputs, add_stats=False):
    def f(*args, extra_outputs_array=extra_outputs, **kwargs):
        ## TODO: 增加内存统计和显示功能
        
        
        try:
            res = list(func(*args, **kwargs))
        except Exception as e:
            print("Error completing request", file=sys.stderr)
            argStr = f"Arguments: {str(args)} {str(kwargs)}"
            max_debug_str_len = 131072
            print(argStr[:max_debug_str_len], file=sys.stderr)
            if len(argStr) > max_debug_str_len:
                print(f"(Argument list truncated at {max_debug_str_len}/{len(argStr)} characters)", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            if extra_outputs_array is not None:
                res += extra_outputs_array
            
        if add_stats:
            ## TODO: 增加显示统计
            ...
        
        return tuple(res)
    return f