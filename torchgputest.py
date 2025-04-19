import torch
from torch.utils import benchmark


typ = torch.float16

n = 1024 * 16
a = torch.randn(n,n).type(typ).cuda()
b = torch.randn(n,n).type(typ).cuda()


t = benchmark.Timer(stmt='a @ b',
                    globals={'a':a, 'b':b})

x = t.timeit(50)
tflops = 2*n**3 / x.median / 1e12

print("TFlops : {:.02f}".format(tflops))
