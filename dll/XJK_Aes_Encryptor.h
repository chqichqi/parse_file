#pragma once
//#define TEST_ARR  1   // 临时统计Arr，并通知调用者报警
#if _MSC_VER >=1500 //vs2008
#include "stdafx.h"
#ifdef DLL_API//如果已经定义就什么都不做
//nothing to do
#else //否则定义DLL_API
#define DLL_API __declspec(dllexport)    //_declspec(dllexport)：导出标志
#endif
#else 
#define DLL_API
#endif //



#include <stdio.h>
#if _MSC_VER !=1500 //非vs2008
#include "stdint.h"
#endif
#include <iostream>

#include "string.h"
using namespace std;
#ifdef XJK_DATAENCRYPTOR_QT_LIBRARY
   #include <QObject>
   #define DLL_API Q_DECL_EXPORT   //_declspec(dllexport)：导出标志
#endif
#define MAX_TIME    4607251200000     //最大时间戳，到2116年1月1日0：0:0，如果实际时间超过这个时间，请修改这个值

#define MIN_TIME    946483200000	  //最小时间戳，1999年12月30日0：0:0,如果有时间早于这个时间，请修改这个值。
									  //JKW手表复位后，默认时间是2010年1月1日0:0:0,,贴心集没有设置时间不能用，所以不存在时间不对的情况。
									  //JKC手表复位后，默认时间是2000年1月1日0:0:0,
#ifdef TEST_ARR
#include "FileHeadStrut.h"
#endif // TEST_ARR




class DLL_API CXJK_Aes_Encryptor
{
public:
	CXJK_Aes_Encryptor();
	~CXJK_Aes_Encryptor();

	/*数据加解密
	参数意义：

	int iMode 加解密模式，0=字符串加解密，1= 数据流加解密，2= 全文件加解密,3=日志加密,4= 重建文件尾（只能针对文件版本 >=3 的文件），5= 加密图片文件（解密图片文件按2= 全文件解密），后端也按文件方式加解密。
	char* cBuffer 输入缓冲，当iMode =0时，传输需要加解密的字符串，当iMode =1时，传输需要加解密的数据流；当iMode =2时，传输需要加解密的文件全路径，也是加解密后的输出缓冲；
	当iMode = 3时，加密日志字符串，加密的日志按字符串输入，然后输出按二进制流的方式存文件。
	当iMode= e_GetPassword （7）获得密码，需要传入文件名（包括扩展名，不包括目录），且输入缓冲长度不低于32个字节，密码是32位的。

	int iBufferLen 输入缓冲的实际内容字节数，加密时，实际缓冲的申请要大于此长度，当iMode =0 时，缓冲长度需要2倍实际字符串长度 +40，当iMode =1时，缓冲长度需要实际数据长度 +24，
	当iMode =2时，文件全路径长度 + 1，当iMode =3时，缓冲长度需要实际数据长度 +256，多余的缓冲清零；解密时需要申请 源数据长度 +16
	string strKey 加密密钥,16字节，前端（手机端和手表端）加密输入""。
	int bLastPacket 是否是最后一包，非最后一包输入要是16的整倍数，最后一包不需要，只有在iMode =1 数据流加解密时有效

	返回值， >0 返回加解密后的数据长度，< 0 错误编码，-1 表示输入的中间包不是16的正倍数，
	-2 表示 开始位置大于文件长度,-3 表示输入的文件是非加密文件，-4 表示输入的是加密的文件。-5  表示非心吉康文件， -6 表示创建临时文件错
	 -7 表示打开源文件错,-8 输入长度为0， -9 输入缓冲为空，-10 输入模式有误,-11 表示错误调用了二次加密，-12 表示没有文件尾,-13 文件尾内容出错,-14表示文件版本太低（‘1’或者‘2’）
	 - 15 包头中数据长度错，-16 表示后端加密前端无法解密,-17 表示文件只有文件头，-18 表示文件只有文件头和包头，-19 图片文件已经加密，不能再次加密,-20 数据包解密出错,-21 数据包的开始时间戳不对,
	 -22 没找到文件夹
	int  bDecrypt2 是否需要二次解密，0=不需要，1 = 需要，解出原始数据。
	注：文件加解密时，文件头、包头和文件尾不加解密，不影响以前的处理方式，文件头中存储加密标志。解密时文件头、包头和文件尾不解密。

	*/

	
	int XJK_Encrypt(int iMode, char* cBuffer, int iBufferLen, string strKey = "", int bLastPacket = 1);
	int XJK_Decrypt(int iMode, char* cBuffer, int iBufferLen, string strKey = "", int  bDecrypt2 = 0, int bLastPacket = 1);
	//获得版本，按1000000表示1.00.00.00
	int GetVer();


private:	
	std::string EncryptString(void *pEncryptor, std::string strInfor);
	std::string DecryptString(void *pEncryptor, std::string strMessage);
	void Byte2Hex(const unsigned char* src, int len, char* dest);
	void Hex2Byte(const char* src, int len, unsigned char* dest);
	int  Char2Int(char c);	
	int XJK_EncryptLog(char* cBuffer, int iBufferLen);	
	int XJK_DecryptLog(char* cBuffer, int iBufferLen);
	int DecryptOneLog(char * pBuffer,int iBufferLen);	
	int DecryptFile(int iMode, char* cBuffer, int iBufferLen, string strKey, bool  bUseFile);
	int EncryptFile(int iMode, char* cBuffer, int iBufferLen, string strKey);
	int EncryptPictureFile(char* cBuffer, int iBufferLen, string strKey);	
	int DecryptOnePacket(int iMode, char* cBuffer, string strKey, int iPackLen,int iNoCheckLen);
	int ReWriteTail(char *cBuffer);
	int GetPassword(char* cBuffer, int iBufferLen);
	int ChangeECG(char* cBuffer, int iBufferLen);
	void ResortData(unsigned char * pbyDataIn, unsigned char *pbyDataOut, int iBytes);
	void AddTxjFileHead(FILE *imgFile, string strID, int iType,int iFileLen, unsigned char TimeID[7]);
#ifdef TEST_ARR
	int CountArr(char* cBuffer, int iBufferLen,int iTimeLen );	
	void MinusArr();
	
	int CountShortArr(int iTimeLen);
#endif
	
private:
	
	unsigned char m_cBaseKey[16];
};

