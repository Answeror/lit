'WinUser.h implementation'

RC_INVOKED = True

from .sdkddkver import _WIN32_IE, _WIN32_WINNT
from .windows import *

# IS_INTRESOURCE and MAKEINTRESOURCE code from pyWinLite project, author Vincent Povirk (2008)
def IS_INTRESOURCE(i):
	try:
		return i.value|0xFFFF == 0xFFFF
	except AttributeError:
		return i|0xFFFF == 0xFFFF
if UNICODE:
	def MAKEINTRESOURCE(i):#MAKEINTRESOURCEW
		return cast(c_void_p(i&0xFFFF), c_wchar_p)
else:
	def MAKEINTRESOURCE(i):#MAKEINTRESOURCEA
		return cast(c_void_p(i&0xFFFF), c_char_p)

# ========================
# some constants from WinUser.h

# Predefined Clipboard Formats
CF_TEXT = 1
CF_BITMAP = 2
CF_METAFILEPICT = 3
CF_SYLK = 4
CF_DIF = 5
CF_TIFF = 6
CF_OEMTEXT = 7
CF_DIB = 8
CF_PALETTE = 9
CF_PENDATA = 10
CF_RIFF = 11
CF_WAVE = 12
CF_UNICODETEXT = 13
CF_ENHMETAFILE = 14
if WINVER >= 0x0400:
	CF_HDROP = 15
	CF_LOCALE = 16
if WINVER >= 0x0500:
	CF_DIBV5 = 17

if WINVER >= 0x0500:
	CF_MAX = 18
elif WINVER >= 0x0400:
	CF_MAX = 17
else:
	CF_MAX = 15

CF_OWNERDISPLAY = 0x0080
CF_DSPTEXT = 0x0081
CF_DSPBITMAP = 0x0082
CF_DSPMETAFILEPICT = 0x0083
CF_DSPENHMETAFILE = 0x008E

# "Private" formats don't get GlobalFree()'d
CF_PRIVATEFIRST = 0x0200
CF_PRIVATELAST = 0x02FF

# "GDIOBJ" formats do get DeleteObject()'d
CF_GDIOBJFIRST = 0x0300
CF_GDIOBJLAST = 0x03FF

# Edit Control Styles
ES_LEFT        = 0x0000
ES_CENTER      = 0x0001
ES_RIGHT       = 0x0002
ES_MULTILINE   = 0x0004
ES_UPPERCASE   = 0x0008
ES_LOWERCASE   = 0x0010
ES_PASSWORD    = 0x0020
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL = 0x0080
ES_NOHIDESEL   = 0x0100
ES_OEMCONVERT  = 0x0400
ES_READONLY    = 0x0800
ES_WANTRETURN  = 0x1000
if WINVER >= 0x0400:
	ES_NUMBER = 0x2000

IMAGE_BITMAP = 0
IMAGE_ICON = 1
IMAGE_CURSOR = 2
if WINVER >= 0x0400:
	IMAGE_ENHMETAFILE = 3

	LR_DEFAULTCOLOR     = 0x00000000
	LR_MONOCHROME       = 0x00000001
	LR_COLOR            = 0x00000002
	LR_COPYRETURNORG    = 0x00000004
	LR_COPYDELETEORG    = 0x00000008
	LR_LOADFROMFILE     = 0x00000010
	LR_LOADTRANSPARENT  = 0x00000020
	LR_DEFAULTSIZE      = 0x00000040
	LR_VGACOLOR         = 0x00000080
	LR_LOADMAP3DCOLORS  = 0x00001000
	LR_CREATEDIBSECTION = 0x00002000
	LR_COPYFROMRESOURCE = 0x00004000
	LR_SHARED           = 0x00008000

	DI_MASK        = 0x0001
	DI_IMAGE       = 0x0002
	DI_NORMAL      = 0x0003
	DI_COMPAT      = 0x0004
	DI_DEFAULTSIZE = 0x0008
	if WINVER >= 0x0501:
		DI_NOMIRROR = 0x0010

	RES_ICON   = 1
	RES_CURSOR = 2


# OEM Resource Ordinal Numbers
# OEM bitmaps
OBM_CLOSE          = 32754
OBM_UPARROW        = 32753
OBM_DNARROW        = 32752
OBM_RGARROW        = 32751
OBM_LFARROW        = 32750
OBM_REDUCE         = 32749
OBM_ZOOM           = 32748
OBM_RESTORE        = 32747
OBM_REDUCED        = 32746
OBM_ZOOMD          = 32745
OBM_RESTORED       = 32744
OBM_UPARROWD       = 32743
OBM_DNARROWD       = 32742
OBM_RGARROWD       = 32741
OBM_LFARROWD       = 32740
OBM_MNARROW        = 32739
OBM_COMBO          = 32738
OBM_UPARROWI       = 32737
OBM_DNARROWI       = 32736
OBM_RGARROWI       = 32735
OBM_LFARROWI       = 32734

OBM_OLD_CLOSE      = 32767
OBM_SIZE           = 32766
OBM_OLD_UPARROW    = 32765
OBM_OLD_DNARROW    = 32764
OBM_OLD_RGARROW    = 32763
OBM_OLD_LFARROW    = 32762
OBM_BTSIZE         = 32761
OBM_CHECK          = 32760
OBM_CHECKBOXES     = 32759
OBM_BTNCORNERS     = 32758
OBM_OLD_REDUCE     = 32757
OBM_OLD_ZOOM       = 32756
OBM_OLD_RESTORE    = 32755

# OEM cursors
OCR_NORMAL         = 32512
OCR_IBEAM          = 32513
OCR_WAIT           = 32514
OCR_CROSS          = 32515
OCR_UP             = 32516
OCR_SIZE           = 32640   # OBSOLETE: use OCR_SIZEALL */
OCR_ICON           = 32641   # OBSOLETE: use OCR_NORMAL */
OCR_SIZENWSE       = 32642
OCR_SIZENESW       = 32643
OCR_SIZEWE         = 32644
OCR_SIZENS         = 32645
OCR_SIZEALL        = 32646
OCR_ICOCUR         = 32647   # OBSOLETE: use OIC_WINLOGO */
OCR_NO             = 32648
if WINVER >= 0x0500:
	OCR_HAND       = 32649
if WINVER >= 0x0400:
	OCR_APPSTARTING = 32650

# OEM icons
OIC_SAMPLE         = 32512
OIC_HAND           = 32513
OIC_QUES           = 32514
OIC_BANG           = 32515
OIC_NOTE           = 32516
if WINVER >= 0x0400:
	OIC_WINLOGO    = 32517
	OIC_WARNING    = OIC_BANG
	OIC_ERROR      = OIC_HAND
	OIC_INFORMATION = OIC_NOTE
if WINVER >= 0x0600:
	OIC_SHIELD     = 32518


# Standard Icon IDs
if RC_INVOKED:
	IDI_APPLICATION    = 32512
	IDI_HAND           = 32513
	IDI_QUESTION       = 32514
	IDI_EXCLAMATION    = 32515
	IDI_ASTERISK       = 32516
	if WINVER >= 0x0400:
		IDI_WINLOGO    = 32517
	if WINVER >= 0x0600:
		IDI_SHIELD     = 32518
else:
	IDI_APPLICATION    = MAKEINTRESOURCE(32512)
	IDI_HAND           = MAKEINTRESOURCE(32513)
	IDI_QUESTION       = MAKEINTRESOURCE(32514)
	IDI_EXCLAMATION    = MAKEINTRESOURCE(32515)
	IDI_ASTERISK       = MAKEINTRESOURCE(32516)
	if WINVER >= 0x0400:
		IDI_WINLOGO    = MAKEINTRESOURCE(32517)
	if WINVER >= 0x0600:
		IDI_SHIELD     = MAKEINTRESOURCE(32518)

if WINVER >= 0x0400:
	IDI_WARNING     = IDI_EXCLAMATION
	IDI_ERROR       = IDI_HAND
	IDI_INFORMATION = IDI_ASTERISK

# Class field offsets for GetClassLong()
GCL_MENUNAME      = -8
GCL_HBRBACKGROUND = -10
GCL_HCURSOR       = -12
GCL_HICON         = -14
GCL_HMODULE       = -16
GCL_CBWNDEXTRA    = -18
GCL_CBCLSEXTRA    = -20
GCL_WNDPROC       = -24
GCL_STYLE         = -26
GCW_ATOM          = -32
if WINVER >= 0x0400:
	GCL_HICONSM = -34

SB_HORZ = 0
SB_VERT = 1
SB_CTL = 2
SB_BOTH = 3

SB_LINEUP           =0
SB_LINELEFT         =0
SB_LINEDOWN         =1
SB_LINERIGHT        =1
SB_PAGEUP           =2
SB_PAGELEFT         =2
SB_PAGEDOWN         =3
SB_PAGERIGHT        =3
SB_THUMBPOSITION    =4
SB_THUMBTRACK       =5
SB_TOP              =6
SB_LEFT             =6
SB_BOTTOM           =7
SB_RIGHT            =7
SB_ENDSCROLL        =8

if WINVER >= 0x0400:
	SIF_RANGE          = 0x0001
	SIF_PAGE           = 0x0002
	SIF_POS            = 0x0004
	SIF_DISABLENOSCROLL= 0x0008
	SIF_TRACKPOS       = 0x0010
	SIF_ALL            = SIF_RANGE | SIF_PAGE | SIF_POS | SIF_TRACKPOS

class SCROLLINFO(Structure):
	_fields_ = [('cbSize', c_uint),
		('fMask', c_uint),
		('nMin', c_int),
		('nMax', c_int),
		('nPage', c_uint),
		('nPos', c_int),
		('nTrackPos', c_int)]
LPSCROLLINFO = POINTER(SCROLLINFO)

if WINVER >= 0x0400:
	WM_NOTIFY                      = 0x004E
	WM_INPUTLANGCHANGEREQUEST      = 0x0050
	WM_INPUTLANGCHANGE             = 0x0051
	WM_TCARD                       = 0x0052
	WM_HELP                        = 0x0053
	WM_USERCHANGED                 = 0x0054
	WM_NOTIFYFORMAT                = 0x0055
	NFR_ANSI                       =      1
	NFR_UNICODE                    =      2
	NF_QUERY                       =      3
	NF_REQUERY                     =      4
	WM_CONTEXTMENU                 = 0x007B
	WM_STYLECHANGING               = 0x007C
	WM_STYLECHANGED                = 0x007D
	WM_DISPLAYCHANGE               = 0x007E
	WM_GETICON                     = 0x007F
	WM_SETICON                     = 0x0080

if WINVER >= 0x0400:
	HELPINFO_WINDOW = 0x0001
	HELPINFO_MENUITEM = 0x0002

GWL_WNDPROC = -4
GWL_HINSTANCE = -6
GWL_HWNDPARENT = -8
GWL_ID = -12
GWL_STYLE = -16
GWL_EXSTYLE = -20
GWL_USERDATA = -21

# GetSystemMetrics() codes
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SM_CXVSCROLL = 2
SM_CYHSCROLL = 3
SM_CYCAPTION = 4
SM_CXBORDER = 5
SM_CYBORDER = 6
SM_CXDLGFRAME = 7
SM_CYDLGFRAME = 8
SM_CYVTHUMB = 9
SM_CXHTHUMB = 10
SM_CXICON = 11
SM_CYICON = 12
SM_CXCURSOR = 13
SM_CYCURSOR = 14
SM_CYMENU = 15
SM_CXFULLSCREEN = 16
SM_CYFULLSCREEN = 17
SM_CYKANJIWINDOW = 18
SM_MOUSEPRESENT = 19
SM_CYVSCROLL = 20
SM_CXHSCROLL = 21
SM_DEBUG = 22
SM_SWAPBUTTON = 23
SM_RESERVED1 = 24
SM_RESERVED2 = 25
SM_RESERVED3 = 26
SM_RESERVED4 = 27
SM_CXMIN = 28
SM_CYMIN = 29
SM_CXSIZE = 30
SM_CYSIZE = 31
SM_CXFRAME = 32
SM_CYFRAME = 33
SM_CXMINTRACK = 34
SM_CYMINTRACK = 35
SM_CXDOUBLECLK = 36
SM_CYDOUBLECLK = 37
SM_CXICONSPACING = 38
SM_CYICONSPACING = 39
SM_MENUDROPALIGNMENT = 40
SM_PENWINDOWS = 41
SM_DBCSENABLED = 42
SM_CMOUSEBUTTONS = 43

if WINVER >= 0x0400:
	SM_CXFIXEDFRAME = SM_CXDLGFRAME # ;win40 name change
	SM_CYFIXEDFRAME = SM_CYDLGFRAME # ;win40 name change
	SM_CXSIZEFRAME = SM_CXFRAME # ;win40 name change
	SM_CYSIZEFRAME = SM_CYFRAME # ;win40 name change

	SM_SECURE = 44
	SM_CXEDGE = 45
	SM_CYEDGE = 46
	SM_CXMINSPACING = 47
	SM_CYMINSPACING = 48
	SM_CXSMICON = 49
	SM_CYSMICON = 50
	SM_CYSMCAPTION = 51
	SM_CXSMSIZE = 52
	SM_CYSMSIZE = 53
	SM_CXMENUSIZE = 54
	SM_CYMENUSIZE = 55
	SM_ARRANGE = 56
	SM_CXMINIMIZED = 57
	SM_CYMINIMIZED = 58
	SM_CXMAXTRACK = 59
	SM_CYMAXTRACK = 60
	SM_CXMAXIMIZED = 61
	SM_CYMAXIMIZED = 62
	SM_NETWORK = 63
	SM_CLEANBOOT = 67
	SM_CXDRAG = 68
	SM_CYDRAG = 69

SM_SHOWSOUNDS = 70
if WINVER >= 0x0400:
	SM_CXMENUCHECK = 71 # Use instead of GetMenuCheckMarkDimensions()
	SM_CYMENUCHECK = 72
	SM_SLOWMACHINE = 73
	SM_MIDEASTENABLED = 74

if WINVER >= 0x0500 and _WIN32_WINNT >= 0x0400:
	SM_MOUSEWHEELPRESENT = 75
if WINVER >= 0x0500:
	SM_XVIRTUALSCREEN = 76
	SM_YVIRTUALSCREEN = 77
	SM_CXVIRTUALSCREEN = 78
	SM_CYVIRTUALSCREEN = 79
	SM_CMONITORS = 80
	SM_SAMEDISPLAYFORMAT = 81
if _WIN32_WINNT >= 0x0500:
	SM_IMMENABLED = 82
if _WIN32_WINNT >= 0x0501:
	SM_CXFOCUSBORDER = 83
	SM_CYFOCUSBORDER = 84

if _WIN32_WINNT >= 0x0501:
	SM_TABLETPC = 86
	SM_MEDIACENTER = 87
	SM_STARTER = 88
	SM_SERVERR2 = 89

if _WIN32_WINNT >= 0x0600:
	SM_MOUSEHORIZONTALWHEELPRESENT = 91
	SM_CXPADDEDBORDER = 92

if WINVER < 0x0500 or _WIN32_WINNT < 0x0400:
	SM_CMETRICS = 76
elif WINVER == 0x500:
	SM_CMETRICS = 83
elif WINVER == 0x501:
	SM_CMETRICS = 90
else:
	SM_CMETRICS = 93

if WINVER >= 0x0500:
	SM_REMOTESESSION = 0x1000

	if _WIN32_WINNT >= 0x0501:
		SM_SHUTTINGDOWN = 0x2000

	if WINVER >= 0x0501:
		SM_REMOTECONTROL = 0x2001
		SM_CARETBLINKINGENABLED = 0x2002

class ICONINFO(Structure):
	_fields_ = [('fIcon', c_bool),
	('xHotspot', c_int),
	('yHotspot', c_int),
	('hbmMask', c_void_p),# HBITMAP
	('hbmColor', c_void_p)]# HBITMAP
PICONINFO = POINTER(ICONINFO)

# Structure pointed to by lParam of WM_HELP
class HELPINFO(Structure):
	_fields_ = [('cbSize', UINT),# Size in bytes of this struct
	('iContextType', c_int),# Either HELPINFO_WINDOW or HELPINFO_MENUITEM
	('iCtrlId', c_int),# Control Id or a Menu item Id.
	('hItemHandle', c_void_p),# hWnd of control or hMenu.
	('dwContextId', c_void_p),# Context Id associated with this item
	('MousePos', LPPOINT)]# Mouse Position in screen co-ordinates
LPHELPINFO = POINTER(HELPINFO)

MSGBOXCALLBACK = WINFUNCTYPE(None, LPHELPINFO)
class MSGBOXPARAMS(Structure):
	_fields_ = [('cbSize', UINT),
	('hwndOwner', c_void_p),
	('hInstance', c_void_p)]
	if UNICODE:
		_fields_ += [('lpszText', c_wchar_p), ('lpszCaption', c_wchar_p)]
	else:
		_fields_+= [('lpszText', c_char_p), ('lpszCaption', c_char_p)]
	_fields_.append(('dwStyle', DWORD))
	if UNICODE:
		_fields_.append(('lpszIcon', c_wchar_p))
	else:
		_fields_.append(('lpszIcon', c_char_p))
	_fields_ += [('dwContextHelpId', c_void_p),
	('lpfnMsgBoxCallback', MSGBOXCALLBACK),
	('dwLanguageId', DWORD)]
LPMSGBOXPARAMS = POINTER(MSGBOXPARAMS)

DLGPROC = WINFUNCTYPE(c_void_p, HWND, UINT, WPARAM, LPARAM)

if UNICODE:
	MessageBox = WINFUNCTYPE(c_int, c_void_p, c_wchar_p, c_wchar_p, c_uint)(('MessageBoxW', windll.user32))
	MessageBoxIndirect = WINFUNCTYPE(c_int, LPMSGBOXPARAMS)(('MessageBoxIndirectW', windll.user32))

	FindWindow = windll.user32.FindWindowW
	SetMenuItemInfo = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_bool, POINTER(MENUITEMINFO))(('SetMenuItemInfoW', windll.user32))
	GetMenuItemInfo = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_bool, POINTER(MENUITEMINFO))(('GetMenuItemInfoW', windll.user32))
	SetWindowsHookEx = windll.user32.SetWindowsHookExW
	RegisterClipboardFormat = windll.user32.RegisterClipboardFormatW
	DialogBoxParam = windll.user32.DialogBoxParamW
	CreateDialogIndirectParam = windll.user32.CreateDialogIndirectParamW
	DialogBoxIndirectParam = windll.user32.DialogBoxIndirectParamW
	GetClassName = WINFUNCTYPE(c_int, c_void_p, c_wchar_p, c_int)(('GetClassNameW', windll.user32))
	GetClassInfo = WINFUNCTYPE(c_bool, c_void_p, c_wchar_p, c_void_p)(('GetClassInfoW', windll.user32))
	GetClassInfoP = windll.user32.GetClassInfoW

	RegisterClassEx = WINFUNCTYPE(c_void_p, POINTER(WNDCLASSEX))(('RegisterClassExW', windll.user32))
	DefWindowProc = WINFUNCTYPE(c_long, c_void_p, c_uint, c_uint, c_long)(('DefWindowProcW', windll.user32))
	CallWindowProc = WINFUNCTYPE(c_long, c_void_p, c_void_p, c_uint, c_uint, c_long)(('CallWindowProcW', windll.user32))
	CreateWindowEx = WINFUNCTYPE(ValidHandle, c_ulong, c_wchar_p, c_wchar_p, c_ulong, c_int, c_int, c_int, c_int, c_void_p, c_void_p, c_void_p, c_void_p)(('CreateWindowExW', windll.user32))
	CreateWindowEx_atom = WINFUNCTYPE(ValidHandle, c_ulong, c_void_p, c_wchar_p, c_ulong, c_int, c_int, c_int, c_int, c_void_p, c_void_p, c_void_p, c_void_p)(('CreateWindowExW', windll.user32))
	AppendMenu = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_uint, c_wchar_p)(('AppendMenuW', windll.user32))
	GetMessage = WINFUNCTYPE(c_bool, c_void_p, c_void_p, c_uint, c_uint)(('GetMessageW', windll.user32))
	SendMessage = WINFUNCTYPE(c_long, c_void_p, c_uint, c_uint, c_void_p)(('SendMessageW', windll.user32))
	PostMessage = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_uint, c_long)(('PostMessageW', windll.user32))
	DispatchMessage = WINFUNCTYPE(c_long, c_void_p)(('DispatchMessageW', windll.user32))
	RegisterWindowMessage = windll.user32.RegisterWindowMessageW
	SetWindowLong = windll.user32.SetWindowLongW
	SetClassLong = WINFUNCTYPE(None, c_void_p, c_int, c_long)(('SetClassLongW', windll.user32))
	GetClassLong = windll.user32.GetClassLongW
	CreateAcceleratorTable = windll.user32.CreateAcceleratorTableW

	SetWindowText = WINFUNCTYPE(c_bool, c_void_p, c_wchar_p)(('SetWindowTextW', windll.user32))
	GetWindowText = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int)(('GetWindowTextW', windll.user32))
	GetWindowTextLength = WINFUNCTYPE(c_int, c_void_p)(('GetWindowTextLengthW', windll.user32))
	#~ LoadIcon = WINFUNCTYPE(HICON, HINSTANCE, c_wchar_p)(('LoadIconW', windll.user32))
	_LoadIcon = WINFUNCTYPE(c_void_p, c_void_p, c_wchar_p)(('LoadIconW', windll.user32))
	_LoadIconP = WINFUNCTYPE(c_void_p, c_void_p, c_int)(('LoadIconW', windll.user32))
	_LoadCursor = WINFUNCTYPE(c_void_p, c_void_p, c_wchar_p)(('LoadCursorW', windll.user32))
	_LoadCursorP = windll.user32.LoadCursorW
	LoadCursorFromFile = WINFUNCTYPE(c_void_p, c_wchar_p)(('LoadCursorFromFileW', windll.user32))
	_LoadImage = WINFUNCTYPE(c_void_p, c_void_p, c_wchar_p, c_uint, c_int, c_int, c_uint)(('LoadImageW', windll.user32))
	_LoadImageP = windll.user32.LoadImageW
	LoadString = WINFUNCTYPE(c_int, c_void_p, c_uint, c_wchar_p, c_int)(('LoadStringW', windll.user32))
else:
	MessageBox = WINFUNCTYPE(c_int, c_void_p, c_char_p, c_char_p, c_uint)(('MessageBoxA', windll.user32))
	MessageBoxIndirect = WINFUNCTYPE(c_int, LPMSGBOXPARAMS)(('MessageBoxIndirectA', windll.user32))

	FindWindow = windll.user32.FindWindowA
	SetMenuItemInfo = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_bool, POINTER(MENUITEMINFO))(('SetMenuItemInfoA', windll.user32))
	GetMenuItemInfo = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_bool, POINTER(MENUITEMINFO))(('GetMenuItemInfoA', windll.user32))
	SetWindowsHookEx = windll.user32.SetWindowsHookExA
	RegisterClipboardFormat = windll.user32.RegisterClipboardFormatA
	DialogBoxParam = windll.user32.DialogBoxParamA
	CreateDialogIndirectParam = windll.user32.CreateDialogIndirectParamA
	DialogBoxIndirectParam = windll.user32.DialogBoxIndirectParamA
	GetClassName = WINFUNCTYPE(c_int, c_void_p, c_char_p, c_int)(('GetClassNameA', windll.user32))
	GetClassInfo = WINFUNCTYPE(c_bool, c_void_p, c_char_p, c_void_p)(('GetClassInfoA', windll.user32))
	GetClassInfoP = windll.user32.GetClassInfoA

	RegisterClassEx = WINFUNCTYPE(c_void_p, POINTER(WNDCLASSEX))(('RegisterClassExA', windll.user32))
	DefWindowProc = WINFUNCTYPE(c_long, c_void_p, c_uint, c_uint, c_long)(('DefWindowProcA', windll.user32))
	CallWindowProc = WINFUNCTYPE(c_long, c_void_p, c_void_p, c_uint, c_uint, c_long)(('CallWindowProcA', windll.user32))
	CreateWindowEx = CreateWindowEx_atom = windll.user32.CreateWindowExA
	AppendMenu = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_uint, c_char_p)(('AppendMenuA', windll.user32))
	GetMessage = WINFUNCTYPE(c_bool, c_void_p, c_void_p, c_uint, c_uint)(('GetMessageA', windll.user32))
	SendMessage = WINFUNCTYPE(c_long, c_void_p, c_uint, c_uint, c_void_p)(('SendMessageA', windll.user32))
	PostMessage = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_uint, c_long)(('PostMessageA', windll.user32))
	DispatchMessage = WINFUNCTYPE(c_long, c_void_p)(('DispatchMessageA', windll.user32))
	RegisterWindowMessage = windll.user32.RegisterWindowMessageA
	SetWindowLong = windll.user32.SetWindowLongA
	SetClassLong = WINFUNCTYPE(None, c_void_p, c_int, c_long)(('SetClassLongA', windll.user32))
	GetClassLong = windll.user32.GetClassLongA
	CreateAcceleratorTable = windll.user32.CreateAcceleratorTableA

	SetWindowText = WINFUNCTYPE(c_bool, c_void_p, c_char_p)(('SetWindowTextA', windll.user32))
	GetWindowText = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int)(('GetWindowTextA', windll.user32))
	GetWindowTextLength = WINFUNCTYPE(c_int, c_void_p)(('GetWindowTextLengthA', windll.user32))
	#~ LoadIcon = WINFUNCTYPE(HICON, HINSTANCE, c_char_p)(('LoadIconA', windll.user32))
	_LoadIcon = WINFUNCTYPE(c_void_p, c_void_p, c_char_p)(('LoadIconA', windll.user32))
	_LoadIconP = WINFUNCTYPE(c_void_p, c_void_p, c_int)(('LoadIconA', windll.user32))
	_LoadCursor = WINFUNCTYPE(c_void_p, c_void_p, c_char_p)(('LoadCursorA', windll.user32))
	_LoadCursorP = windll.user32.LoadCursorA
	LoadCursorFromFile = WINFUNCTYPE(c_void_p, c_char_p)(('LoadCursorFromFileA', windll.user32))
	_LoadImage = WINFUNCTYPE(c_void_p, c_void_p, c_char_p, c_uint, c_int, c_int, c_uint)(('LoadImageA', windll.user32))
	_LoadImageP = windll.user32.LoadImageA
	LoadString = WINFUNCTYPE(c_int, c_void_p, c_uint, c_wchar_p, c_int)(('LoadStringA', windll.user32))

CreateIcon = WINFUNCTYPE(HICON, HINSTANCE, c_int, c_int, c_byte, c_byte, c_void_p, c_void_p)(('CreateIcon', windll.user32))
CreateIconIndirect = WINFUNCTYPE(HICON, PICONINFO)(('CreateIconIndirect', windll.user32))
CopyIcon = WINFUNCTYPE(HICON, HICON)(('CopyIcon', windll.user32))
_GetIconInfo = WINFUNCTYPE(c_bool, HICON, PICONINFO)(('GetIconInfo', windll.user32))
def GetIconInfo():
	info = ICONINFO()
	result = _GetIconInfo(info)
	return result, info

#WINUSERAPI int WINAPI ExcludeUpdateRgn(__in HDC hDC, __in HWND hWnd);
ExcludeUpdateRgn = WINFUNCTYPE(c_int, c_void_p, c_void_p)(('ExcludeUpdateRgn', windll.user32))

InvalidateRect = WINFUNCTYPE(c_bool, c_void_p, POINTER(RECT), c_bool)(('InvalidateRect', windll.user32))
InvalidateRgn = WINFUNCTYPE(c_bool, c_void_p, c_void_p, c_bool)(('InvalidateRect', windll.user32))
ValidateRect = WINFUNCTYPE(c_bool, c_void_p, POINTER(RECT))(('ValidateRect', windll.user32))
ValidateRgn = WINFUNCTYPE(c_bool, c_void_p, c_void_p)(('ValidateRgn', windll.user32))

#Static Control Constants
SS_LEFT = 0x00000000
#~ SS_SIMPLE = 0x0000000BL
SS_SIMPLE = 0x0000000B

def LoadIcon(hInstance = None, file_or_resource = 0):
	if isinstance(file_or_resource,  int):
		return _LoadIconP(hInstance, file_or_resource)
	else:
		return _LoadIcon(hInstance, file_or_resource)

def LoadCursor(hInstance = None, file_or_resource = 0):
	if isinstance(file_or_resource,  int):
		return _LoadCursorP(hInstance, file_or_resource)
	else:
		return _LoadCursor(hInstance, file_or_resource)

def LoadImage(hInstance = None, file_or_resource = 0, img_type = 0, x = 0, y = 0, uFlags = 0):
	if isinstance(file_or_resource,  int):
		return _LoadImageP(hInstance, file_or_resource, img_type, x, y, uFlags)
	else:
		return _LoadImage(hInstance, file_or_resource, img_type, x, y, uFlags)

DrawIcon = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, c_void_p)(('DrawIcon', windll.user32))
DrawIconEx = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, c_void_p, c_int, c_int, c_uint, c_void_p, c_uint)(('DrawIconEx', windll.user32))

AttachThreadInput = WINFUNCTYPE(c_bool, c_void_p, c_void_p, c_bool)(('AttachThreadInput', windll.user32))
GetWindowThreadProcessId = WINFUNCTYPE(DWORD, c_void_p, c_void_p)(('GetWindowThreadProcessId', windll.user32))

MoveWindow = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, c_int, c_int, c_bool)(('MoveWindow', windll.user32))
MapDialogRect = WINFUNCTYPE(c_bool, c_void_p, LPRECT)(('MapDialogRect', windll.user32))
GetSystemMetrics = WINFUNCTYPE(c_int, c_int)(('GetSystemMetrics', windll.user32))
GetDialogBaseUnits = WINFUNCTYPE(c_long)(('GetDialogBaseUnits', windll.user32))

ShowCursor = WINFUNCTYPE(c_int, c_bool)(('ShowCursor', windll.user32))
SetCursorPos = WINFUNCTYPE(c_bool, c_int, c_int)(('SetCursorPos', windll.user32))
#~ SetPhysicalCursorPos = WINFUNCTYPE(c_bool, c_int, c_int)(('SetPhysicalCursorPos', windll.user32))
SetCursor = WINFUNCTYPE(c_void_p, c_void_p)(('SetCursor', windll.user32))
GetCursor = WINFUNCTYPE(c_void_p)(('GetCursor', windll.user32))
SetSystemCursor = WINFUNCTYPE(c_bool, c_void_p, c_ulong)(('SetSystemCursor', windll.user32))
GetCursorPosP = WINFUNCTYPE(c_bool, c_void_p)(('GetCursorPos', windll.user32))
_GetCursorPos = WINFUNCTYPE(c_bool, LPPOINT)(('GetCursorPos', windll.user32))
def GetCursorPos():
	point = POINT()
	result = _GetCursorPos(point)
	return result, point
#~ _GetPhysicalCursorPos = WINFUNCTYPE(c_bool, LPPOINT)(('GetPhysicalCursorPos', windll.user32))
#~ def GetPhysicalCursorPos():
	#~ point = POINT()
	#~ result = _GetPhysicalCursorPos(point)
	#~ return result, point
ClipCursor = WINFUNCTYPE(c_bool, LPRECT)(('ClipCursor', windll.user32), ((3, 'rect'), ))
#~ def ClipCursor(rect = None):
	#~ return _ClipCursor(rect)
_GetClipCursor = WINFUNCTYPE(c_bool, LPRECT)(('GetClipCursor', windll.user32))
def GetClipCursor():
	rect = RECT()
	result = _GetClipCursor(rect)
	return result, rect

ShowWindow = windll.user32.ShowWindow
UpdateWindow = WINFUNCTYPE(c_bool, c_void_p)(('UpdateWindow', windll.user32))
SetActiveWindow = WINFUNCTYPE(c_void_p, c_void_p)(('SetActiveWindow', windll.user32))
GetForegroundWindow = WINFUNCTYPE(c_void_p)(('GetForegroundWindow', windll.user32))
SetForegroundWindow = WINFUNCTYPE(c_bool, c_void_p)(('SetForegroundWindow', windll.user32))
if WINVER >= 0x0400:
	PaintDesktop = WINFUNCTYPE(c_bool, c_void_p)(('PaintDesktop', windll.user32))
	SwitchToThisWindow = WINFUNCTYPE(None, c_void_p, c_bool)(('SwitchToThisWindow', windll.user32))

ChildWindowFromPoint = windll.user32.ChildWindowFromPoint
TranslateMessage = windll.user32.TranslateMessage
GetWindowRect = windll.user32.GetWindowRect
DestroyWindow = windll.user32.DestroyWindow
CloseWindow = windll.user32.CloseWindow
CreateMenu = windll.user32.CreateMenu
CreatePopupMenu = windll.user32.CreatePopupMenu
DestroyMenu = windll.user32.DestroyMenu
EnableMenuItem = windll.user32.EnableMenuItem
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
IsDialogMessage = windll.user32.IsDialogMessage
GetParent = windll.user32.GetParent
SetWindowPos = windll.user32.SetWindowPos
BeginPaint = windll.user32.BeginPaint
EndPaint = windll.user32.EndPaint
SetCapture = windll.user32.SetCapture
GetCapture = windll.user32.GetCapture
ReleaseCapture = windll.user32.ReleaseCapture
ScreenToClient = windll.user32.ScreenToClient
ClientToScreen = windll.user32.ClientToScreen

#WINUSERAPI BOOL WINAPI ScrollWindow(__in HWND hWnd, __in int XAmount, __in int YAmount, __in_opt CONST RECT *lpRect, __in_opt CONST RECT *lpClipRect);
ScrollWindow = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, LPRECT, LPRECT)(('ScrollWindow', windll.user32))

#WINUSERAPI BOOL WINAPI ScrollDC(__in HDC hDC, __in int dx, __in int dy, __in_opt CONST RECT *lprcScroll, __in_opt CONST RECT *lprcClip, __in_opt HRGN hrgnUpdate, __out_opt LPRECT lprcUpdate);
ScrollDC = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, LPRECT, LPRECT, c_void_p, LPRECT)(('ScrollDC', windll.user32))

#WINUSERAPI int WINAPI ScrollWindowEx(__in HWND hWnd, __in int dx, __in int dy, __in_opt CONST RECT *prcScroll, __in_opt CONST RECT *prcClip, __in_opt HRGN hrgnUpdate, __out_opt LPRECT prcUpdate, __in UINT flags);
ScrollWindowEx = WINFUNCTYPE(c_int, c_void_p, c_int, c_int, LPRECT, LPRECT, c_void_p, LPRECT, c_uint)(('ScrollWindowEx', windll.user32))

#WINUSERAPI int WINAPI SetScrollInfo(__in HWND hwnd, __in int nBar, __in LPCSCROLLINFO lpsi, __in BOOL redraw);
SetScrollInfo = WINFUNCTYPE(c_int, c_void_p, c_int, LPSCROLLINFO, c_bool)(('SetScrollInfo', windll.user32))

#WINUSERAPI BOOL WINAPI GetScrollInfo(__in HWND hwnd, __in int nBar, __inout LPSCROLLINFO lpsi);
_GetScrollInfo = WINFUNCTYPE(c_bool, c_void_p, c_int, LPSCROLLINFO)(('GetScrollInfo', windll.user32))
def GetScrollInfo(hwnd, nBar = SB_CTL, fMask = SIF_ALL):
	scroll_info_size = sizeof(SCROLLINFO)
	#~ scroll_info = cast(GlobalAlloc(0, scroll_info_size), LPSCROLLINFO)
	scroll_info = SCROLLINFO()
	#~ ZeroMemory(scroll_info, scroll_info_size)
	scroll_info.cbSize = scroll_info_size
	scroll_info.fMask = fMask
	result = _GetScrollInfo(hwnd, nBar, scroll_info)
	return result, scroll_info

#WINUSERAPI int WINAPI SetScrollPos(__in HWND hWnd, __in int nBar, __in int nPos, __in BOOL bRedraw);
SetScrollPos = WINFUNCTYPE(c_int, c_void_p, c_int, c_int, c_bool)(('SetScrollPos', windll.user32))

#WINUSERAPI int WINAPI GetScrollPos(__in HWND hWnd, __in int nBar);
GetScrollPos = WINFUNCTYPE(c_int, c_void_p, c_int)(('GetScrollPos', windll.user32))

#WINUSERAPI BOOL WINAPI SetScrollRange(__in HWND hWnd, __in int nBar, __in int nMinPos, __in int nMaxPos, __in BOOL bRedraw);
SetScrollRange = WINFUNCTYPE(c_bool, c_void_p, c_int, c_int, c_int, c_bool)(('SetScrollRange', windll.user32))

#WINUSERAPI BOOL WINAPI GetScrollRange(__in HWND hWnd, __in int nBar, __out LPINT lpMinPos, __out LPINT lpMaxPos);
_GetScrollRange = WINFUNCTYPE(c_bool, c_void_p, c_int, c_void_p, c_void_p)(('GetScrollRange', windll.user32))
def GetScrollRange(hwnd, nBar = SB_CTL):
	lpMinPos = c_int()
	lpMaxPos = c_int()
	result = _GetScrollRange(hwnd, nBar, byref(lpMinPos), byref(lpMaxPos))
	return result, lpMinPos.value, lpMaxPos.value

#WINUSERAPI BOOL WINAPI ShowScrollBar(__in HWND hWnd, __in int wBar, __in BOOL bShow);
ShowScrollBar = WINFUNCTYPE(c_bool, c_void_p, c_int, c_bool)(('ShowScrollBar', windll.user32))

#WINUSERAPI BOOL WINAPI EnableScrollBar(__in HWND hWnd, __in UINT wSBflags, __in UINT wArrows);
EnableScrollBar = WINFUNCTYPE(c_bool, c_void_p, c_uint, c_uint)(('EnableScrollBar', windll.user32))

#WINUSERAPI BOOL WINAPI EnumChildWindows(__in_opt HWND hWndParent, __in WNDENUMPROC lpEnumFunc, __in LPARAM lParam);
WNDENUMPROC = WINFUNCTYPE(c_bool, c_void_p, c_ulong)
EnumChildWindows = WINFUNCTYPE(c_bool, c_void_p, WNDENUMPROC, c_ulong)(('EnumChildWindows', windll.user32))

OpenClipboard = WINFUNCTYPE(c_bool, c_void_p)(('OpenClipboard', windll.user32))
EmptyClipboard = WINFUNCTYPE(c_bool)(('EmptyClipboard', windll.user32))
CloseClipboard = WINFUNCTYPE(c_bool)(('CloseClipboard', windll.user32))
SetClipboardData = WINFUNCTYPE(c_void_p, c_uint, c_void_p)(('SetClipboardData', windll.user32))
GetClipboardData = windll.user32.GetClipboardData
EnumClipboardFormats = windll.user32.EnumClipboardFormats
IsClipboardFormatAvailable = windll.user32.IsClipboardFormatAvailable

def text_to_clipboard(self, hwnd = 0, text = ''):
	'idealy insert this func to your own Window class code and change hwnd to self.handle'
	if OpenClipboard(hwnd):
		TCHAR = c_char
		data_type = CF_TEXT
		if isinstance(text, type_unicode):
			TCHAR = c_wchar
			data_type = CF_UNICODETEXT
		if EmptyClipboard():
			# Allocate a global memory object for the text
			hglb_size = (len(text) + 1) * sizeof(TCHAR)
			hglb_copy = GlobalAlloc(GMEM_MOVEABLE, hglb_size)
			if hglb_copy:
				# Lock the handle and copy the text to the buffer
				lptstr_copy = GlobalLock(hglb_copy)
				memcpy(lptstr_copy, text, hglb_size)
				GlobalUnlock(hglb_copy)
				# send data to clipboard
				SetClipboardData(data_type, hglb_copy)
				# free a global memory object handle
				GlobalFree(hglb_copy)
		else:
			print('ERROR CLEAR OLD CLIPBOARD DATA')
		if not CloseClipboard():
			print('ERROR CLOSE CLIPBOARD')
	else:
		print('ERROR OPEN CLIPBOARD')
