#------------------------------------------------
#--- Ghost of Tsushima [PC] - ".sps" plugin for Rich Whitehouse's Noesis
#
#      File: fmt_GoT_SPS.py
#    Author: SilverEzredes
#   Version: May 25, 2024 - v1.0.5
#   Purpose: To import and export Ghost of Tsushima .sps files
#   Credits: alphaZomega
#------------------------------------------------
#--- Options:
isGoTSPSExport  =   True    #Enable or disable export of .sps from the export list.
isDebug         =   False   #Enable or disable debug mode.
isFlipImage     =   True    #If set to True, textures will be flipped upright on import then flipped upside down again on export.
#------------------------------------------------
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Ghost of Tsushima Texture [PC]", ".sps")
    noesis.setHandlerTypeCheck(handle, spsCheckType)
    noesis.setHandlerLoadRGBA(handle, spsLoadRGBA)

    if isGoTSPSExport:
        handle = noesis.register("Ghost of Tsushima Texture [PC]", ".sps")
        noesis.setHandlerTypeCheck(handle, spsCheckType)
        noesis.setHandlerWriteRGBA(handle, spsWriteRGBA)
          
    noesis.logPopup()
    return 1

def spsCheckType(data):
	bs = NoeBitStream(data)
     
	magic = bs.readUInt()
	if magic == 1396855896:
		return 1
	else: 
		print("Fatal Error: Unknown file magic: " + str(hex(magic) + " expected XTBS!"))
		return 0

def spsLoadRGBA(data, texList):
    bs = NoeBitStream(data)

    magic = bs.readUInt()
    version = bs.readUInt()
    bs.seek(16, 1)
    textureDataOffset = bs.readUInt()
    bs.seek(4, 1)
    textureNameLenght = bs.readUInt()
    bs.seek(textureNameLenght, 1)
    bs.seek(20, 1)
    dxgiFormat = bs.readUInt()
    if isDebug:
        print("DXGI Format: ", dxgiFormat)
    width = bs.readUShort()
    height = bs.readUShort()
    depth = bs.readUShort()
    mipMapCount = bs.readUShort()
    print("Texture Height: ", height, "| Texture Width: ", width, "| MipMap Count: ", mipMapCount)
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
    elif dxgiFormat == 251661824 or dxgiFormat == 251727360:
        texData = bs.readBytes(width*height)
        texData = rapi.imageDecodeDXT(texData, width, height, noesis.FOURCC_BC7)
        print("Format: BC7_UNORM_SRGB")
    elif dxgiFormat == 251723776:
        texData = bs.readBytes(width*height*4)
        texData = rapi.imageDecodeRaw(texData, width, height, "B8G8R8A8")
        print("Format: B8G8R8A8_UNORM")
    else:
        print("FATAL ERROR: Unsupported texture type!")
        return 0
    
    if isFlipImage:
        texData = rapi.imageFlipRGBA32(texData, width, height, 0, 1)
        print("Image Flip Enabled")

    sps = NoeTexture("GoT.sps", width, height, texData, noesis.NOESISTEX_RGBA32)
    texList.append(sps)

    return 1

def spsWriteRGBA(data, width, height, bs):
    
    def getExportName(fileName):		
        if fileName == None:
            newSpsName = rapi.getInputName()
        else:
            newSpsName = fileName
        newSpsName =  newSpsName.lower().replace(".spsout","").replace(".sps","").replace(".dds","").replace("out.",".").replace(".jpg","").replace(".png","").replace(".tga","")
        newSpsName = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Export over the original sps", "Select the original sps file to export over", newSpsName + ".sps", None)
        if newSpsName == None:
            print("Aborting...")
            return
        return newSpsName
    
    fileName = None
    newSpsName = getExportName(fileName)
    if newSpsName == None:
        return 0
    while not (rapi.checkFileExists(newSpsName)):
        print ("File not found")
        newSpsName = getExportName(fileName)	
        fileName = newSpsName
        if newSpsName == None:
            return 0
        
    newSPS = rapi.loadIntoByteArray(newSpsName)
    oldDDS = rapi.loadIntoByteArray(rapi.getInputName())
    f = NoeBitStream(newSPS)
    og = NoeBitStream(oldDDS)
    
    magic = f.readUInt()
    if magic != 1396855896:
        print ("Selected file is not an sps file!\nAborting...")
        return 0
    f.seek(20, 1)
    textureDataOffset = f.readUInt()
    f.seek(4, 1)
    textureNameLenght = f.readUInt()
    f.seek(textureNameLenght, 1)
    f.seek(20, 1)
    dxgiFormat = f.readUInt()

    f.seek(0)
    bs.writeBytes(f.readBytes(textureDataOffset))
    
    mipWidth = width
    mipHeight = height
    
    print ("----| Ghost of Tsushima Texture Export |----")
    if isFlipImage:
         print("Image Flip Enabled")
    if isDebug:
        print ("Writing Image Data at:", bs.tell())

    while mipWidth >= 1 and mipHeight >= 1:
        mipData = rapi.imageResample(data, width, height, mipWidth, mipHeight)
        
        if isFlipImage:
            mipData = rapi.imageFlipRGBA32(mipData, mipWidth, mipHeight, 0, 1)

        if dxgiFormat == 251723776:
            dxtData = rapi.imageEncodeRaw(data, mipWidth, mipHeight, "B8G8R8A8_UNORM")
        elif dxgiFormat == 251725312:
            dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, noesis.FOURCC_BC1)
        elif dxgiFormat == 251725824:
            dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, noesis.FOURCC_BC3)
        elif dxgiFormat == 251660544 or dxgiFormat == 251791616 or dxgiFormat == 251726080:
            dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, noesis.FOURCC_BC4)
        elif dxgiFormat == 251660800 or dxgiFormat == 251923200:
            dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, noesis.FOURCC_BC5)
        elif dxgiFormat == 251661824 or dxgiFormat == 251727360:
            dxtData = rapi.imageEncodeDXT(mipData, 4, mipWidth, mipHeight, noesis.FOURCC_BC7)

        bs.writeBytes(dxtData)
        
        if mipWidth == 1 and mipHeight == 1:
            break
        if mipWidth > 1:
            mipWidth = int(mipWidth / 2)
        if mipHeight > 1:
            mipHeight = int(mipHeight / 2)
            
    return 1