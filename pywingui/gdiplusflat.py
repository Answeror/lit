# gdiplusflat.py created from gdiplusflat.h
# Copyright (c) 2012 Maxim Kolosov

GDIPVER = 0x0100

# enum Status
Status = 0
Ok = 0
GenericError = 1
InvalidParameter = 2
OutOfMemory = 3
ObjectBusy = 4
InsufficientBuffer = 5
NotImplemented = 6
Win32Error = 7
WrongState = 8
Aborted = 9
FileNotFound = 10
ValueOverflow = 11
AccessDenied = 12
UnknownImageFormat = 13
FontFamilyNotFound = 14
FontStyleNotFound = 15
NotTrueTypeFont = 16
UnsupportedGdiplusVersion = 17
GdiplusNotInitialized = 18
PropertyNotFound = 19
PropertyNotSupported = 20
if GDIPVER >= 0x0110:
    ProfileNotFound = 21

# enum Unit constants
Unit = 0
UnitWorld = 0# World coordinate (non-physical unit)
UnitDisplay = 1# Variable -- for PageTransform only
UnitPixel = 2# Each unit is one device pixel.
UnitPoint = 3# Each unit is a printer's point, or 1/72 inch.
UnitInch = 4# Each unit is 1 inch.
UnitDocument = 5# Each unit is 1/300 inch.
UnitMillimeter = 6# Each unit is 1 millimeter.

# enum GdiplusStartupParams
GdiplusStartupParams = 0
GdiplusStartupDefault = 0
GdiplusStartupNoSetRound = 1
GdiplusStartupSetPSValue = 2
GdiplusStartupTransparencyMask = 0xFF000000

AlphaShift  = 24
RedShift    = 16
GreenShift  = 8
BlueShift   = 0

AlphaMask = 0xff000000
RedMask   = 0x00ff0000
GreenMask = 0x0000ff00
BlueMask  = 0x000000ff

def MakeARGB(a, r, g, b):
	return c_ulong((b <<  BlueShift) | (g << GreenShift) | (r <<   RedShift) | (a << AlphaShift))

from ctypes import *

DebugEventProc = WINFUNCTYPE(None, c_int, c_char_p)
NotificationHookProc = WINFUNCTYPE(c_int, c_void_p)
NotificationUnhookProc = WINFUNCTYPE(None, c_void_p)

class GdiplusStartupInput(Structure):
	'startup_input = GdiplusStartupInput(1, None, False, False)'
	_fields_ = [('GdiplusVersion', c_uint),
	('DebugEventCallback', DebugEventProc),
	('SuppressBackgroundThread', c_bool),
	('SuppressExternalCodecs', c_bool)]

class GdiplusStartupOutput(Structure):
	_fields_ = [('NotificationHook', NotificationHookProc),
	('NotificationUnhook', NotificationUnhookProc)]

#extern "C" Status WINAPI GdiplusStartup(OUT ULONG_PTR *token, const GdiplusStartupInput *input, OUT GdiplusStartupOutput *output);
GdiplusStartup = WINFUNCTYPE(c_int, c_void_p, POINTER(GdiplusStartupInput), c_void_p)(('GdiplusStartup', windll.gdiplus))

#extern "C" VOID WINAPI GdiplusShutdown(ULONG_PTR token);
GdiplusShutdown = WINFUNCTYPE(None, c_void_p)(('GdiplusShutdown', windll.gdiplus))


#=========
# Brush APIs

#GpStatus WINGDIPAPI GdipCloneBrush(GpBrush *brush, GpBrush **cloneBrush);
_GdipCloneBrush = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipCloneBrush', windll.gdiplus))
def GdipCloneBrush(brush):
	cloneBrush = c_void_p()
	status = _GdipCloneBrush(brush, byref(cloneBrush))
	return status, cloneBrush

#GpStatus WINGDIPAPI GdipDeleteBrush(GpBrush *brush);
GdipDeleteBrush = WINFUNCTYPE(c_int, c_void_p)(('GdipDeleteBrush', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetBrushType(GpBrush *brush, GpBrushType *type);
_GdipGetBrushType = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetBrushType', windll.gdiplus))
def GdipGetBrushType(brush):
	type_brush = c_int()
	status = _GdipGetBrushType(brush, byref(type_brush))
	return status, type_brush.value


#========
# SolidBrush APIs

#GpStatus WINGDIPAPI GdipCreateSolidFill(ARGB color, GpSolidFill **brush);
_GdipCreateSolidFill = WINFUNCTYPE(c_int, c_ulong, c_void_p)(('GdipCreateSolidFill', windll.gdiplus))
def GdipCreateSolidFill(color = 128):
	brush = c_void_p()
	status = _GdipCreateSolidFill(color, byref(brush))
	return status, brush

#GpStatus WINGDIPAPI GdipSetSolidFillColor(GpSolidFill *brush, ARGB color);
GdipSetSolidFillColor = WINFUNCTYPE(c_int, c_void_p, c_ulong)(('GdipSetSolidFillColor', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetSolidFillColor(GpSolidFill *brush, ARGB *color);
_GdipGetSolidFillColor = WINFUNCTYPE(c_int, c_ulong, c_void_p)(('GdipGetSolidFillColor', windll.gdiplus))
def GdipGetSolidFillColor(brush):
	color = c_ulong()
	status = _GdipGetSolidFillColor(brush, byref(color))
	return status, color.value


#========
# Pen APIs

#GpStatus WINGDIPAPI GdipCreatePen1(ARGB color, REAL width, GpUnit unit, GpPen **pen);
_GdipCreatePen1 = WINFUNCTYPE(c_int, c_ulong, c_float, c_int, c_void_p)(('GdipCreatePen1', windll.gdiplus))
def GdipCreatePen1(color = MakeARGB(255, 255, 255, 255), width = 1.0, unit = UnitWorld):
	pen = c_void_p()
	status = _GdipCreatePen1(color, width, unit, byref(pen))
	return status, pen

#GpStatus WINGDIPAPI GdipCreatePen2(GpBrush *brush, REAL width, GpUnit unit, GpPen **pen);
_GdipCreatePen2 = WINFUNCTYPE(c_int, c_void_p, c_float, c_int, c_void_p)(('GdipCreatePen2', windll.gdiplus))
def GdipCreatePen2(color = None, width = 1.0, unit = UnitWorld):
	pen = c_void_p()
	status = _GdipCreatePen2(color, width, unit, byref(pen))
	return status, pen

#GpStatus WINGDIPAPI GdipClonePen(GpPen *pen, GpPen **clonepen);
_GdipClonePen = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipClonePen', windll.gdiplus))
def GdipClonePen(pen):
	clonepen = c_void_p()
	status = _GdipClonePen(pen, byref(clonepen))
	return status, clonepen

#GpStatus WINGDIPAPI GdipDeletePen(GpPen *pen);
GdipDeletePen = WINFUNCTYPE(c_int, c_void_p)(('GdipDeletePen', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSetPenWidth(GpPen *pen, REAL width);
GdipSetPenWidth = WINFUNCTYPE(c_int, c_void_p, c_float)(('GdipSetPenWidth', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetPenWidth(GpPen *pen, REAL *width);
_GdipGetPenWidth = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetPenWidth', windll.gdiplus))
def GdipGetPenWidth(pen):
	width = c_float()
	status = _GdipGetPenWidth(pen, byref(width))
	return status, width.value

#GpStatus WINGDIPAPI GdipSetPenUnit(GpPen *pen, GpUnit unit);
GdipSetPenUnit = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetPenUnit', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetPenUnit(GpPen *pen, GpUnit *unit);
_GdipGetPenUnit = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetPenUnit', windll.gdiplus))
def GdipGetPenUnit(pen):
	unit = c_int()
	status = _GdipGetPenUnit(pen, byref(unit))
	return status, unit.value


#=========
# Image APIs

#GpStatus WINGDIPAPI GdipLoadImageFromStream(IStream* stream, GpImage **image);
_GdipLoadImageFromStream = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipLoadImageFromStream', windll.gdiplus))
def GdipLoadImageFromStream(stream):
	image = c_void_p()
	status = _GdipLoadImageFromStream(stream, byref(image))
	return status, image

#GpStatus WINGDIPAPI GdipLoadImageFromFile(GDIPCONST WCHAR* filename, GpImage **image);
_GdipLoadImageFromFile = WINFUNCTYPE(c_int, c_wchar_p, c_void_p)(('GdipLoadImageFromFile', windll.gdiplus))
def GdipLoadImageFromFile(filename = ''):
	image = c_void_p()
	status = _GdipLoadImageFromFile(filename, byref(image))
	return status, image

#GpStatus WINGDIPAPI GdipLoadImageFromStreamICM(IStream* stream, GpImage **image);
_GdipLoadImageFromStreamICM = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipLoadImageFromStreamICM', windll.gdiplus))
def GdipLoadImageFromStreamICM(stream):
	image = c_void_p()
	status = _GdipLoadImageFromStreamICM(stream, byref(image))
	return status, image

#GpStatus WINGDIPAPI GdipLoadImageFromFileICM(GDIPCONST WCHAR* filename, GpImage **image);
_GdipLoadImageFromFileICM = WINFUNCTYPE(c_int, c_wchar_p, c_void_p)(('GdipLoadImageFromFileICM', windll.gdiplus))
def GdipLoadImageFromFileICM(filename = ''):
	image = c_void_p()
	status = _GdipLoadImageFromFileICM(filename, byref(image))
	return status, image

#GpStatus WINGDIPAPI GdipCloneImage(GpImage *image, GpImage **cloneImage);
_GdipCloneImage = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipCloneImage', windll.gdiplus))
def GdipCloneImage(image):
	cloneImage = c_void_p()
	status = _GdipCloneImage(image, byref(cloneImage))
	return status, cloneImage

#GpStatus WINGDIPAPI GdipDisposeImage(GpImage *image);
GdipDisposeImage = WINFUNCTYPE(c_int, c_void_p)(('GdipDisposeImage', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSaveImageToFile(GpImage *image, GDIPCONST WCHAR* filename, GDIPCONST CLSID* clsidEncoder, GDIPCONST EncoderParameters* encoderParams);
GdipSaveImageToFile = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_void_p)(('GdipSaveImageToFile', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSaveImageToStream(GpImage *image, IStream* stream, GDIPCONST CLSID* clsidEncoder, GDIPCONST EncoderParameters* encoderParams);
GdipSaveImageToStream = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_void_p)(('GdipSaveImageToStream', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSaveAdd(GpImage *image, GDIPCONST EncoderParameters* encoderParams);
GdipSaveAdd = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipSaveAdd', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSaveAddImage(GpImage *image, GpImage* newImage, GDIPCONST EncoderParameters* encoderParams);
GdipSaveAddImage = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)(('GdipSaveAddImage', windll.gdiplus))


#===========
# Graphics APIs

#GpStatus WINGDIPAPI GdipFlush(GpGraphics *graphics, GpFlushIntention intention);
GdipFlush = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipFlush', windll.gdiplus))

#GpStatus WINGDIPAPI GdipCreateFromHDC(HDC hdc, GpGraphics **graphics);
_GdipCreateFromHDC = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipCreateFromHDC', windll.gdiplus))
def GdipCreateFromHDC(hdc):
	graphics = c_void_p()
	status = _GdipCreateFromHDC(hdc, byref(graphics))
	return status, graphics

#GpStatus WINGDIPAPI GdipCreateFromHDC2(HDC hdc, HANDLE hDevice, GpGraphics **graphics);
GdipCreateFromHDC2 = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)(('GdipCreateFromHDC2', windll.gdiplus))

#GpStatus WINGDIPAPI GdipCreateFromHWND(HWND hwnd, GpGraphics **graphics);
GdipCreateFromHWND = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipCreateFromHWND', windll.gdiplus))

#GpStatus WINGDIPAPI GdipCreateFromHWNDICM(HWND hwnd, GpGraphics **graphics);
GdipCreateFromHWNDICM = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipCreateFromHWNDICM', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDeleteGraphics(GpGraphics *graphics);
GdipDeleteGraphics = WINFUNCTYPE(c_int, c_void_p)(('GdipDeleteGraphics', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetDC(GpGraphics* graphics, HDC * hdc);
_GdipGetDC = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetDC', windll.gdiplus))
def GdipGetDC(graphics):
	hdc = c_void_p()
	status = _GdipGetDC(graphics, byref(hdc))
	return status, hdc

#GpStatus WINGDIPAPI GdipReleaseDC(GpGraphics* graphics, HDC hdc);
GdipReleaseDC = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipReleaseDC', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSetCompositingMode(GpGraphics *graphics, CompositingMode compositingMode);
GdipSetCompositingMode = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetCompositingMode', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetCompositingMode(GpGraphics *graphics, CompositingMode *compositingMode);
_GdipGetCompositingMode = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetCompositingMode', windll.gdiplus))
def GdipGetCompositingMode(graphics):
	compositingMode = c_int()
	status = _GdipGetCompositingMode(graphics, byref(compositingMode))
	return status, compositingMode.value

#GpStatus WINGDIPAPI GdipSetRenderingOrigin(GpGraphics *graphics, INT x, INT y);
GdipSetRenderingOrigin = WINFUNCTYPE(c_int, c_void_p, c_int, c_int)(('GdipSetRenderingOrigin', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetRenderingOrigin(GpGraphics *graphics, INT *x, INT *y);
_GdipGetRenderingOrigin = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p)(('GdipGetRenderingOrigin', windll.gdiplus))
def GdipGetRenderingOrigin(graphics):
	x, y = c_int(), c_int()
	status = _GdipGetRenderingOrigin(graphics, byref(x), byref(y))
	return status, x.value, y.value

#GpStatus WINGDIPAPI GdipSetCompositingQuality(GpGraphics *graphics, CompositingQuality compositingQuality);
GdipSetCompositingQuality = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetCompositingQuality', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetCompositingQuality(GpGraphics *graphics, CompositingQuality *compositingQuality);
_GdipGetCompositingQuality = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetCompositingQuality', windll.gdiplus))
def GdipGetCompositingQuality(graphics):
	compositingQuality = c_int()
	status = _GdipGetCompositingQuality(graphics, byref(compositingQuality))
	return status, compositingQuality.value

#GpStatus WINGDIPAPI GdipSetSmoothingMode(GpGraphics *graphics, SmoothingMode smoothingMode);
GdipSetSmoothingMode = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetSmoothingMode', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetSmoothingMode(GpGraphics *graphics, SmoothingMode *smoothingMode);
_GdipGetSmoothingMode = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetSmoothingMode', windll.gdiplus))
def GdipGetSmoothingMode(graphics):
	smoothingMode = c_int()
	status = _GdipGetSmoothingMode(graphics, byref(smoothingMode))
	return status, smoothingMode.value

#GpStatus WINGDIPAPI GdipSetPixelOffsetMode(GpGraphics* graphics, PixelOffsetMode pixelOffsetMode);
GdipSetPixelOffsetMode = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetPixelOffsetMode', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetPixelOffsetMode(GpGraphics *graphics, PixelOffsetMode *pixelOffsetMode);
_GdipGetPixelOffsetMode = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetPixelOffsetMode', windll.gdiplus))
def GdipGetPixelOffsetMode(graphics):
	pixelOffsetMode = c_int()
	status = _GdipGetPixelOffsetMode(graphics, byref(pixelOffsetMode))
	return status, pixelOffsetMode.value

#GpStatus WINGDIPAPI GdipSetTextRenderingHint(GpGraphics *graphics, TextRenderingHint mode);
GdipSetTextRenderingHint = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetTextRenderingHint', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetTextRenderingHint(GpGraphics *graphics, TextRenderingHint *mode);
_GdipGetTextRenderingHint = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetTextRenderingHint', windll.gdiplus))
def GdipGetTextRenderingHint(graphics):
	mode = c_int()
	status = _GdipGetTextRenderingHint(graphics, byref(mode))
	return status, mode.value

#GpStatus  WINGDIPAPI GdipSetTextContrast(GpGraphics *graphics, UINT contrast);
GdipSetTextContrast = WINFUNCTYPE(c_int, c_void_p, c_uint)(('GdipSetTextContrast', windll.gdiplus))

#GpStatus  WINGDIPAPI GdipGetTextContrast(GpGraphics *graphics, UINT * contrast);
_GdipGetTextContrast = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetTextContrast', windll.gdiplus))
def GdipGetTextContrast(graphics):
	contrast = c_uint()
	status = _GdipGetTextContrast(graphics, byref(contrast))
	return status, contrast.value

#GpStatus WINGDIPAPI GdipSetInterpolationMode(GpGraphics *graphics, InterpolationMode interpolationMode);
GdipSetInterpolationMode = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetInterpolationMode', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetInterpolationMode(GpGraphics *graphics, InterpolationMode *interpolationMode);
_GdipGetInterpolationMode = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetInterpolationMode', windll.gdiplus))
def GdipGetInterpolationMode(graphics):
	interpolationMode = c_int()
	status = _GdipGetInterpolationMode(graphics, byref(interpolationMode))
	return status, interpolationMode.value

#GpStatus WINGDIPAPI GdipSetWorldTransform(GpGraphics *graphics, GpMatrix *matrix);
GdipSetWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipSetWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipResetWorldTransform(GpGraphics *graphics);
GdipResetWorldTransform = WINFUNCTYPE(c_int, c_void_p)(('GdipResetWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipMultiplyWorldTransform(GpGraphics *graphics, GDIPCONST GpMatrix *matrix, GpMatrixOrder order);
GdipMultiplyWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int)(('GdipMultiplyWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipTranslateWorldTransform(GpGraphics *graphics, REAL dx, REAL dy, GpMatrixOrder order);
GdipTranslateWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_float, c_float, c_int)(('GdipTranslateWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipScaleWorldTransform(GpGraphics *graphics, REAL sx, REAL sy, GpMatrixOrder order);
GdipScaleWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_float, c_float, c_int)(('GdipScaleWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipRotateWorldTransform(GpGraphics *graphics, REAL angle, GpMatrixOrder order);
GdipRotateWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_float, c_int)(('GdipRotateWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetWorldTransform(GpGraphics *graphics, GpMatrix *matrix);
GdipGetWorldTransform = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetWorldTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipResetPageTransform(GpGraphics *graphics);
GdipResetPageTransform = WINFUNCTYPE(c_int, c_void_p)(('GdipResetPageTransform', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetPageUnit(GpGraphics *graphics, GpUnit *unit);
GdipGetPageUnit = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetPageUnit', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetPageScale(GpGraphics *graphics, REAL *scale);
GdipGetPageScale = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetPageScale', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSetPageUnit(GpGraphics *graphics, GpUnit unit);
GdipSetPageUnit = WINFUNCTYPE(c_int, c_void_p, c_int)(('GdipSetPageUnit', windll.gdiplus))

#GpStatus WINGDIPAPI GdipSetPageScale(GpGraphics *graphics, REAL scale);
GdipSetPageScale = WINFUNCTYPE(c_int, c_void_p, c_float)(('GdipSetPageScale', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetDpiX(GpGraphics *graphics, REAL* dpi);
GdipGetDpiX = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetDpiX', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetDpiY(GpGraphics *graphics, REAL* dpi);
GdipGetDpiY = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetDpiY', windll.gdiplus))

#GpStatus WINGDIPAPI GdipTransformPoints(GpGraphics *graphics, GpCoordinateSpace destSpace, GpCoordinateSpace srcSpace, GpPointF *points, INT count);
GdipTransformPoints = WINFUNCTYPE(c_int, c_void_p, c_int, c_int, c_void_p, c_int)(('GdipTransformPoints', windll.gdiplus))

#GpStatus WINGDIPAPI GdipTransformPointsI(GpGraphics *graphics, GpCoordinateSpace destSpace, GpCoordinateSpace srcSpace, GpPoint *points, INT count);
GdipTransformPointsI = WINFUNCTYPE(c_int, c_void_p, c_int, c_int, c_void_p, c_int)(('GdipTransformPointsI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipGetNearestColor(GpGraphics *graphics, ARGB* argb);
GdipGetNearestColor = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('GdipGetNearestColor', windll.gdiplus))

# Creates the Win9x Halftone Palette (even on NT) with correct Desktop colors
#HPALETTE WINGDIPAPI GdipCreateHalftonePalette();
GdipCreateHalftonePalette = WINFUNCTYPE(c_void_p)(('GdipCreateHalftonePalette', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawLine(GpGraphics *graphics, GpPen *pen, REAL x1, REAL y1, REAL x2, REAL y2);
GdipDrawLine = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float)(('GdipDrawLine', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawLineI(GpGraphics *graphics, GpPen *pen, INT x1, INT y1, INT x2, INT y2);
GdipDrawLineI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int)(('GdipDrawLineI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawLines(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPointF *points, INT count);
GdipDrawLines = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawLines', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawLinesI(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPoint *points, INT count);
GdipDrawLinesI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawLinesI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawArc(GpGraphics *graphics, GpPen *pen, REAL x, REAL y, REAL width, REAL height, REAL startAngle, REAL sweepAngle);
GdipDrawArc = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float, c_float, c_float)(('GdipDrawArc', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawArcI(GpGraphics *graphics, GpPen *pen, INT x, INT y, INT width, INT height, REAL startAngle, REAL sweepAngle);
GdipDrawArcI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int, c_float, c_float)(('GdipDrawArcI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawBezier(GpGraphics *graphics, GpPen *pen, REAL x1, REAL y1, REAL x2, REAL y2, REAL x3, REAL y3, REAL x4, REAL y4);
GdipDrawBezier = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float, c_float, c_float, c_float, c_float)(('GdipDrawBezier', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawBezierI(GpGraphics *graphics, GpPen *pen, INT x1, INT y1, INT x2, INT y2, INT x3, INT y3, INT x4, INT y4);
GdipDrawBezierI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int)(('GdipDrawBezierI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawBeziers(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPointF *points, INT count);
GdipDrawBeziers = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawBeziers', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawBeziersI(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPoint *points, INT count);
GdipDrawBeziersI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawBeziersI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawRectangle(GpGraphics *graphics, GpPen *pen, REAL x, REAL y, REAL width, REAL height);
GdipDrawRectangle = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float)(('GdipDrawRectangle', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawRectangleI(GpGraphics *graphics, GpPen *pen, INT x, INT y, INT width, INT height);
GdipDrawRectangleI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int)(('GdipDrawRectangleI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawRectangles(GpGraphics *graphics, GpPen *pen, GDIPCONST GpRectF *rects, INT count);
GdipDrawRectangles = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawRectangles', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawRectanglesI(GpGraphics *graphics, GpPen *pen, GDIPCONST GpRect *rects, INT count);
GdipDrawRectanglesI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawRectanglesI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawEllipse(GpGraphics *graphics, GpPen *pen, REAL x, REAL y, REAL width, REAL height);
GdipDrawEllipse = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float)(('GdipDrawEllipse', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawEllipseI(GpGraphics *graphics, GpPen *pen, INT x, INT y, INT width, INT height);
GdipDrawEllipseI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int)(('GdipDrawEllipseI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawPie(GpGraphics *graphics, GpPen *pen, REAL x, REAL y, REAL width, REAL height, REAL startAngle, REAL sweepAngle);
GdipDrawPie = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float)(('GdipDrawPie', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawPieI(GpGraphics *graphics, GpPen *pen, INT x, INT y, INT width, INT height, REAL startAngle, REAL sweepAngle);
GdipDrawPieI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int, c_float, c_float)(('GdipDrawPieI', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawPolygon(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPointF *points, INT count);
GdipDrawPolygon = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawPolygon', windll.gdiplus))

#GpStatus WINGDIPAPI GdipDrawPolygonI(GpGraphics *graphics, GpPen *pen, GDIPCONST GpPoint *points, INT count);
GdipDrawPolygonI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_void_p, c_int)(('GdipDrawPolygonI', windll.gdiplus))


#...........
#GpStatus WINGDIPAPI GdipFillEllipse(GpGraphics *graphics, GpBrush *brush, REAL x, REAL y, REAL width, REAL height);
GdipFillEllipse = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_float, c_float, c_float, c_float)(('GdipFillEllipse', windll.gdiplus))

#GpStatus WINGDIPAPI GdipFillEllipseI(GpGraphics *graphics, GpBrush *brush, INT x, INT y, INT width, INT height);
GdipFillEllipseI = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_int, c_int, c_int)(('GdipFillEllipseI', windll.gdiplus))
