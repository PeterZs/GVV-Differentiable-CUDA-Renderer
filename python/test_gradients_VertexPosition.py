
########################################################################################################################
# Imports
########################################################################################################################

import tensorflow as tf
from sys import platform
import data.test_mesh_tensor as test_mesh_tensor
import data.test_SH_tensor as test_SH_tensor
import CudaRenderer
import utils.CheckGPU as CheckGPU
import cv2 as cv
import utils.OBJReader as OBJReader
import utils.CameraReader as CameraReader
import numpy as np

########################################################################################################################
# Load custom operators
########################################################################################################################

RENDER_OPERATORS_PATH = ""
if platform == "linux" or platform == "linux2":
    RENDER_OPERATORS_PATH = "../cpp/binaries/Linux/Release/libCustomTensorFlowOperators.so"
elif platform == "win32" or platform == "win64":
    RENDER_OPERATORS_PATH = "../cpp/binaries/Win64/Release/CustomTensorFlowOperators.dll"
customOperators = tf.load_op_library(RENDER_OPERATORS_PATH)

########################################################################################################################
# CudaRendererGpu class
########################################################################################################################

cameraReader = CameraReader.CameraReader('data/cameras.calibration')
testSHCoeff = test_SH_tensor.getSHCoeff(cameraReader.numberOfCameras)
objreader = OBJReader.OBJReader('data/cone.obj')
objreaderMod = OBJReader.OBJReader('data/coneMod.obj')

########################################################################################################################
# Test color function
########################################################################################################################

def test_color_gradient():

    VertexPosConst=tf.constant([objreader.vertexCoordinates],dtype=tf.float32)
    VertexColorConst=tf.constant([objreader.vertexColors],dtype=tf.float32)
    VertexTextureConst=tf.constant([objreader.textureMap],dtype=tf.float32)
    SHCConst = tf.constant(testSHCoeff,dtype=tf.float32)

    rendererTarget = CudaRenderer.CudaRendererGpu(
                                        faces_attr                   = objreader.facesVertexId,
                                        texCoords_attr               = objreader.textureCoordinates,
                                        numberOfVertices_attr        = len(objreader.vertexCoordinates),
                                        extrinsics_attr              = cameraReader.extrinsics ,
                                        intrinsics_attr              = cameraReader.intrinsics,
                                        renderResolutionU_attr       = 1024,
                                        renderResolutionV_attr       = 1024,
                                        renderMode_attr              = 'vertexColor',

                                        vertexPos_input              = VertexPosConst,
                                        vertexColor_input            = VertexColorConst,
                                        texture_input                = VertexTextureConst,
                                        shCoeff_input                = SHCConst
                                        )
    target = rendererTarget.getRenderBufferTF()

    ####
    constThreshold = tf.constant(0.0, tf.float32, [1024, 1024])
    summedUp = tf.reduce_sum(target, 4)  # check G B are black
    maskInverse = tf.greater(summedUp, constThreshold)
    maskFloat = tf.cast(maskInverse, tf.float32)
    maskFloat = tf.reshape(maskFloat, [1, 14, 1024, 1024, 1])
    maskFloat = tf.tile(maskFloat, [1, 1, 1, 1, 3])

    ####
    VertexPosition_rnd = tf.Variable([objreaderMod.vertexCoordinates])

    opt = tf.keras.optimizers.SGD(learning_rate=100.0)

    for i in range(3000):

        with tf.GradientTape() as tape:
            tape.watch(VertexPosition_rnd)
            renderer = CudaRenderer.CudaRendererGpu(
                faces_attr=objreader.facesVertexId,
                texCoords_attr=objreader.textureCoordinates,
                numberOfVertices_attr=len(objreader.vertexCoordinates),
                extrinsics_attr=cameraReader.extrinsics,
                intrinsics_attr=cameraReader.intrinsics,
                renderResolutionU_attr=1024,
                renderResolutionV_attr=1024,
                renderMode_attr='vertexColor',

                vertexPos_input=VertexPosition_rnd,
                vertexColor_input=VertexColorConst,
                texture_input=VertexTextureConst,
                shCoeff_input=SHCConst
            )

            output = renderer.getRenderBufferTF()

            Loss1 = (output-target) * (output-target) * maskFloat
            Loss = tf.reduce_sum(Loss1) / (float(cameraReader.numberOfCameras) * float(objreader.numberOfVertices))

        #apply gradient
        Color_Grad = tape.gradient(Loss,VertexPosition_rnd)
        opt.apply_gradients(zip([Color_Grad],[VertexPosition_rnd]))

        # print loss
        print(i, Loss.numpy())

        #output images
        outputCV = renderer.getRenderBufferOpenCV(0,0)
        targetCV = rendererTarget.getRenderBufferOpenCV(0,0)

        combined = targetCV
        cv.addWeighted(outputCV,0.8,targetCV,0.2,0.0,combined)
        cv.imshow('combined',combined)
        cv.waitKey(1)

########################################################################################################################
# main
########################################################################################################################

freeGPU = CheckGPU.get_free_gpu()

if freeGPU:
    test_color_gradient()   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    