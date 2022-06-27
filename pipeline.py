import kfp
from kfp import dsl
from kfp.components import func_to_container_op, InputPath, OutputPath, create_component_from_func

#@func_to_container_op
def calculate_k(i: int = 10000) -> list:
    # temp = {
    #     'k': 0
    # }
    lst = []
    for j in range(i):
        k = j*2+1
        lst.append(k)
    return lst

#@func_to_container_op
def calculate_value(k: int) -> float:
    i = (k-1)/2
    value = 0
    if i % 2 == 0:
        value = 4/k
    else:
        value = -4/k
    
    return value

#@func_to_container_op
def sum_up(l: list) -> float:
    sum = 0
    for e in l:
        sum += e
    return sum

# @dsl.pipeline(name="test-pipeline")
# def pipeline():
#     get_k = calck_op()
#     lst = []
#     with dsl.ParallelFor(get_k.output) as item:
#         lst.append(calcpi_op(item.k).output)
#     pi = sum_op(lst)

def run():
    k_lst = calculate_k()
    lst = []
    for k in k_lst:
        lst.append(calculate_value(k))
    print(sum_up(lst))


if __name__ == '__main__':
    # calck_op = create_component_from_func(calculate_k, base_image='python:3.9')
    # calcpi_op = create_component_from_func(calculate_value, base_image='python:3.9')
    # sum_op = create_component_from_func(sum_up, base_image='python:3.9')
    # kfp.compiler.Compiler().compile(pipeline, __file__.split(".")[0] + '.yaml')
    run()