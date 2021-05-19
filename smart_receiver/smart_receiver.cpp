
// smart_receiver.cpp: 애플리케이션에 대한 클래스 동작을 정의합니다.
//

#include "pch.h"
#include "framework.h"
#include "smart_receiver.h"
#include "smart_receiverDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// CSApp

BEGIN_MESSAGE_MAP(CSApp, CWinApp)
	ON_COMMAND(ID_HELP, &CWinApp::OnHelp)
END_MESSAGE_MAP()


// CSApp 생성

CSApp::CSApp() : m_bRunStatus(FALSE)
{
	// TODO: 여기에 생성 코드를 추가합니다.
	// InitInstance에 모든 중요한 초기화 작업을 배치합니다.
}


// 유일한 CSApp 개체입니다.

CSApp theApp;


// CSApp 초기화

BOOL CSApp::InitInstance()
{
	// 애플리케이션 매니페스트가 ComCtl32.dll 버전 6 이상을 사용하여 비주얼 스타일을
	// 사용하도록 지정하는 경우, Windows XP 상에서 반드시 InitCommonControlsEx()가 필요합니다.
	// InitCommonControlsEx()를 사용하지 않으면 창을 만들 수 없습니다.
	INITCOMMONCONTROLSEX InitCtrls;
	InitCtrls.dwSize = sizeof(InitCtrls);
	// 응용 프로그램에서 사용할 모든 공용 컨트롤 클래스를 포함하도록
	// 이 항목을 설정하십시오.
	InitCtrls.dwICC = ICC_WIN95_CLASSES;
	InitCommonControlsEx(&InitCtrls);

	CWinApp::InitInstance();

	if (!AfxSocketInit())
	{
		AfxMessageBox(IDP_SOCKETS_INIT_FAILED);
		return FALSE;
	}


	// 대화 상자에 셸 트리 뷰 또는
	// 셸 목록 뷰 컨트롤이 포함되어 있는 경우 셸 관리자를 만듭니다.
	CShellManager *pShellManager = new CShellManager;

	// MFC 컨트롤의 테마를 사용하기 위해 "Windows 원형" 비주얼 관리자 활성화
	CMFCVisualManager::SetDefaultManager(RUNTIME_CLASS(CMFCVisualManagerWindows));

	// 표준 초기화
	// 이들 기능을 사용하지 않고 최종 실행 파일의 크기를 줄이려면
	// 아래에서 필요 없는 특정 초기화
	// 루틴을 제거해야 합니다.
	// 해당 설정이 저장된 레지스트리 키를 변경하십시오.
	// TODO: 이 문자열을 회사 또는 조직의 이름과 같은
	// 적절한 내용으로 수정해야 합니다.
	SetRegistryKey(_T("로컬 애플리케이션 마법사에서 생성된 애플리케이션"));

	CSDlg dlg;
	m_pMainWnd = &dlg;
	INT_PTR nResponse = dlg.DoModal();
	if (nResponse == IDOK)
	{
		// TODO: 여기에 [확인]을 클릭하여 대화 상자가 없어질 때 처리할
		//  코드를 배치합니다.
	}
	else if (nResponse == IDCANCEL)
	{
		// TODO: 여기에 [취소]를 클릭하여 대화 상자가 없어질 때 처리할
		//  코드를 배치합니다.
	}
	else if (nResponse == -1)
	{
		TRACE(traceAppMsg, 0, "경고: 대화 상자를 만들지 못했으므로 애플리케이션이 예기치 않게 종료됩니다.\n");
		TRACE(traceAppMsg, 0, "경고: 대화 상자에서 MFC 컨트롤을 사용하는 경우 #define _AFX_NO_MFC_CONTROLS_IN_DIALOGS를 수행할 수 없습니다.\n");
	}

	// 위에서 만든 셸 관리자를 삭제합니다.
	if (pShellManager != nullptr)
	{
		delete pShellManager;
	}

#if !defined(_AFXDLL) && !defined(_AFX_NO_MFC_CONTROLS_IN_DIALOGS)
	ControlBarCleanUp();
#endif

	// 대화 상자가 닫혔으므로 응용 프로그램의 메시지 펌프를 시작하지 않고  응용 프로그램을 끝낼 수 있도록 FALSE를
	// 반환합니다.
	return FALSE;
}



// 백그라운드 소켓 스레드 작업자 함수
UINT CSApp::SocketThreadFunc(LPVOID lpParam)
{
	// TODO: 여기에 구현 코드 추가.
	CSocket udpSocket;
	CSApp* pApp = (CSApp*)AfxGetApp();
	BYTE recvBuf[1024];
	CString strAddr;
	UINT nPort;

	auto DrawDesktop = []() -> VOID
	{
		CWnd desktopWnd;
		desktopWnd.Attach(GetDesktopWindow());
		CRect desktopRect;
		desktopWnd.GetWindowRect(&desktopRect);

		CDC* lpDesktopDC = desktopWnd.GetDC();
		CDC desktopCopyDC;
		desktopCopyDC.CreateCompatibleDC(lpDesktopDC);
		CBitmap desktopCopyBitmap;
		desktopCopyBitmap.CreateCompatibleBitmap(lpDesktopDC, desktopRect.Width(), desktopRect.Height());
		CBitmap* lpOldDesktopBit = desktopCopyDC.SelectObject(&desktopCopyBitmap);
		desktopCopyDC.BitBlt(0, 0, desktopRect.Width(), desktopRect.Height(), lpDesktopDC, 0, 0, SRCCOPY);
		CDC blandDC;
		blandDC.CreateCompatibleDC(lpDesktopDC);
		CBrush colorBrush;
		colorBrush.CreateSolidBrush(RGB(255, 0, 0));
		CBitmap blandBitmap;
		blandBitmap.CreateCompatibleBitmap(lpDesktopDC, desktopRect.Width(), desktopRect.Height());
		CBitmap* lpOldBlandBIt = blandDC.SelectObject(&blandBitmap);
		blandDC.FillRect(&desktopRect, &colorBrush);

		BLENDFUNCTION bf;
		bf.BlendOp = AC_SRC_OVER;
		bf.BlendFlags = 0;
		bf.SourceConstantAlpha = 10; //0:투명 ~ 255:불투명
		bf.AlphaFormat = 0;

		for (INT a = 0; a < 10; a++)
		{
			lpDesktopDC->AlphaBlend(0, 0, desktopRect.Width(), desktopRect.Height()
				, &blandDC, 0, 0, desktopRect.Width(), desktopRect.Height(), bf);
			Sleep(10);
		}

		Sleep(100);
		lpDesktopDC->BitBlt(0, 0, desktopRect.Width(), desktopRect.Height(), &desktopCopyDC, 0, 0, SRCCOPY);
		blandDC.SelectObject(lpOldBlandBIt);
		desktopCopyDC.SelectObject(lpOldDesktopBit);
		desktopWnd.ReleaseDC(lpDesktopDC);
		desktopWnd.Detach();

		return;
	};


	udpSocket.Create(9500, SOCK_DGRAM);
	for (;;)
	{
		if (WaitForSingleObject(pApp->m_ExitEvent.m_hObject, 0) == WAIT_OBJECT_0)
			break;

		ULONG nReadAbleCount = 0;
		if (ioctlsocket(udpSocket.m_hSocket, FIONREAD, &nReadAbleCount) == SOCKET_ERROR
			|| nReadAbleCount <= 0)
		{
			Sleep(100);
			continue;
		}

		INT nRecvCount = udpSocket.ReceiveFrom(recvBuf, sizeof(recvBuf), strAddr, nPort);
		if (nRecvCount == SOCKET_ERROR)
		{
			Sleep(100);
			continue;
		}

		if (nRecvCount > 0)
		{
			if (lstrcmpW((WCHAR*)recvBuf, L"detect") == 0)
				DrawDesktop();
			else if (lstrcmpW((WCHAR*)recvBuf, L"not detect") == 0)
				;
		}
	}

	//PlaySound(NULL, 0, 0);
	udpSocket.Close();


	return 0;
}
