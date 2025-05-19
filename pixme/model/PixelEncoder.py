from __future__ import annotations

import torch
from torch import nn

from dataclasses import dataclass

D_LATENT: int = 24
D_KERNEL: int = 16

class Conv2DDownsampler(nn.Module):
    @dataclass
    class Config:
        d_latent: int
        d_in: int
        d_kernel: int
        f_downsample: int

        # Non-user defined properties
        @property
        def d_out(self): return self.d_in//self.f_downsample

    def __init__(self, config: Conv2DDownsampler.Config = None):
        super().__init__()
        self.__cfg = config
        self.conv = nn.Conv2d(
            in_channels=self.__cfg.d_latent,
            out_channels=self.__cfg.d_latent,
            kernel_size=self.__cfg.d_kernel,
            padding=self.__cfg.d_kernel//2,
        )
        self.pool = nn.MaxPool2d(self.__cfg.f_downsample)
        self.act = nn.GELU()

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        x = self.conv(img)
        x = self.pool(x)
        x = self.act(x)
        return x


class PixelEncoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.latent = nn.Linear(4, D_LATENT)
        self.samp256 = Conv2DDownsampler(Conv2DDownsampler.Config(
            d_latent=D_LATENT,
            d_in=256,
            d_kernel=D_KERNEL,
            f_downsample=2
        ))
        samp128 = Conv2DDownsampler(Conv2DDownsampler.Config(
            d_latent=D_LATENT,
            d_in=128,
            d_kernel=D_KERNEL,
            f_downsample=2
        ))
        samp64 = Conv2DDownsampler(Conv2DDownsampler.Config(
            d_latent=D_LATENT,
            d_in=64,
            d_kernel=D_KERNEL,
            f_downsample=2
        ))
        samp32 = Conv2DDownsampler(Conv2DDownsampler.Config(
            d_latent=D_LATENT,
            d_in=32,
            d_kernel=D_KERNEL,
            f_downsample=2
        ))

