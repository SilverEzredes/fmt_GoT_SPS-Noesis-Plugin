#------------------------------------------------
#--- Ghost of Tsushima [PC] - ".sps" plugin for Rich Whitehouse's Noesis
#
#      File: fmt_GoT_SPS.py
#    Author: SilverEzredes
#   Version: May 20, 2024 - v1.0.0
#   Purpose: To import and export Ghost of Tsushima .sps files
#   Credits: alphaZomega
#------------------------------------------------

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ghost of Tsushima Texture [PC]", ".sps")
    noesis.setHandlerTypeCheck(handle, CheckType)
    noesis.setHandlerLoadRGBA(handle, LoadRGBA)

    noesis.logPopup()
    return 1

def CheckType(data):
    return 1

def LoadRGBA(data, texList):
    bs = NoeBitStream(data)

    magic = bs.readUInt()
    version = bs.readUInt()
    bs.seek(16, 1)
    TextureDataOffset = bs.readUInt()
    #print(TextureDataOffset)
    bs.seek(4, 1)
    TextureNameLenght = bs.readUInt()
    bs.seek(TextureNameLenght, 1)
    bs.seek(20, 1)
    dxgiFormat = bs.readUInt()
    print("DXGI Format: ", dxgiFormat)
    width = bs.readUShort()
    print("Texture Width: ", width)
    height = bs.readUShort()
    print("Texture Height: ",height)
    Depth = bs.readUShort()
    MipMapCount = bs.readUShort()
    print("MipMap Count: ",MipMapCount)
    bs.seek(4, 1)
    
    if dxgiFormat == 251725312:
        texData = bs.readBytes(width*height // 2)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC1)
        print("Format: BC1_UNORM_SRGB")
    elif dxgiFormat == 251725824:
        texData = bs.readBytes(width*height)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC3)
        print("Format: BC3_UNORM_SRGB")
    elif dxgiFormat == 251660544 or dxgiFormat == 251791616 or dxgiFormat == 251726080:
        texData = bs.readBytes(width*height // 2)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC4)
        print("Format: BC4_UNORM")
    elif dxgiFormat == 251660800 or dxgiFormat == 251923200:
        texData = bs.readBytes(width*height)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC5)
        print("Format: BC5_UNORM")
    elif dxgiFormat == 251661824:
        texData = bs.readBytes(width*height)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
        print("Format: BC7_UNORM_SRGB")
    else:
        print("FATAL ERROR: Unsupported texture type!")
        return 0
    
    sps = NoeTexture("GoT.sps", width, height, texData, noesis.NOESISTEX_RGBA32)
    texList.append(sps)

    return 1
