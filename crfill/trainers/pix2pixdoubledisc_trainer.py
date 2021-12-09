"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""
import pdb
from models.networks.sync_batchnorm import DataParallelWithCallback
import models
import models.arrange_model


class Pix2PixDoubleDiscTrainer:
    """
    Trainer creates the model and optimizers, and uses them to
    updates the weights of the network while reporting losses
    and the latest visuals to visualize the progress in training.
    """

    def __init__(self, opt):
        self.opt = opt
        self.model = models.create_model(opt)
        # self.model = models.arrange_model.ArrangeModel(opt=opt)
        if len(opt.gpu_ids) > 0:
            self.model = DataParallelWithCallback(self.model, device_ids=opt.gpu_ids)
            self.model_on_one_gpu = self.model.module
        else:
            self.model_on_one_gpu = self.model

        self.generated = None
        self.inputs = None
        if opt.isTrain:
            (
                self.optimizer_G,
                self.optimizer_D,
                self.optimizer_DRCNN,
            ) = self.model_on_one_gpu.create_optimizers(opt)
            self.old_lr = opt.lr

    def run_generator_one_step(self, data, i):
        self.optimizer_G.zero_grad()
        self.optimizer_DRCNN.zero_grad()  # reset gradients over rcnn
        g_losses, inputs, generated = self.model(data, mode="generator")
        g_loss = sum(g_losses.values()).mean()
        g_loss.backward()
        self.optimizer_G.step()
        self.g_losses = g_losses
        self.generated = generated
        self.inputs = inputs

    def run_discriminator_one_step(self, data, i):
        self.d_losses = {}
        if not self.opt.no_gan_loss:
            self.optimizer_D.zero_grad()
            d_losses, inputs = self.model(data, mode="discriminator")
            d_loss = sum(d_losses.values()).mean()
            d_loss.backward()
            self.optimizer_D.step()
            self.d_losses = d_losses

    def get_latest_losses(self):
        if not self.opt.freeze_D:
            return {**self.g_losses, **self.d_losses}
        else:
            return self.g_losses

    def get_latest_generated(self):
        return self.generated

    def get_latest_inputs(self):
        return self.inputs

    def update_learning_rate(self, epoch):
        self.update_learning_rate(epoch)

    def save(self, epoch):
        self.model_on_one_gpu.save(epoch)

    ##################################################################
    # Helper functions
    ##################################################################

    def update_learning_rate(self, epoch):
        if epoch > self.opt.niter:
            lrd = self.opt.lr / self.opt.niter_decay
            new_lr = self.old_lr - lrd
        else:
            new_lr = self.old_lr

        if new_lr != self.old_lr:
            if self.opt.no_TTUR:
                new_lr_G = new_lr
                new_lr_D = new_lr
            else:
                new_lr_G = new_lr / 2
                new_lr_D = new_lr * 2

            for param_group in self.optimizer_D.param_groups:
                param_group["lr"] = new_lr_D
            for param_group in self.optimizer_G.param_groups:
                param_group["lr"] = new_lr_G
            print("update learning rate: %f -> %f" % (self.old_lr, new_lr))
            self.old_lr = new_lr
