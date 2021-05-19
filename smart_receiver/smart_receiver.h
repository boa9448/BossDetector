
// smart_receiver.h: PROJECT_NAME 애플리케이션에 대한 주 헤더 파일입니다.
//

#pragma once

#ifndef __AFXWIN_H__
	#error "PCH에 대해 이 파일을 포함하기 전에 'pch.h'를 포함합니다."
#endif

#include "resource.h"		// 주 기호입니다.


// CSApp:
// 이 클래스의 구현에 대해서는 smart_receiver.cpp을(를) 참조하세요.
//

class CSApp : public CWinApp
{
public:
	CSApp();

// 재정의입니다.
public:
	virtual BOOL InitInstance();

// 구현입니다.

	DECLARE_MESSAGE_MAP()
public:
	// 백그라운드 소켓 스레드
	CWinThread* m_lpSocketThread;
	// 백그라운드 소켓 스레드 작업자 함수
	static UINT SocketThreadFunc(LPVOID lpParam);
	// 프로그램 종료 이벤트
	CEvent m_ExitEvent;
	//프로그램 작동 상태
	BOOL m_bRunStatus;
};

extern CSApp theApp;
