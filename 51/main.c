/*
 * STC89C516 任务完成率显示器
 * 功能：
 * 1. 通过动态数码管显示任务完成进度百分比
 * 2. 通过蜂鸣器播放提示音（模拟end.mp3效果）
 * 3. 通过串口接收来自电脑的任务完成率数据
 */

#include <intrins.h> 
#include <REGX52.H>

// 引脚定义
#define DIG_PORT P0    // 数码管段选接在P0口
#define WEI_PORT P1    // 数码管位选接在P1口
#define BUZZER_PORT P3 // 蜂鸣器接在P3口
#define BUZZER_BIT 7   // 蜂鸣器接在P3的第7位

// 使用位操作控制蜂鸣器
#define BUZZER_ON BUZZER_PORT &= ~(1 << BUZZER_BIT)
#define BUZZER_OFF BUZZER_PORT |= (1 << BUZZER_BIT)
#define BUZZER_TOGGLE BUZZER_PORT ^= (1 << BUZZER_BIT)

// 位掩码定义
#define WEI1_MASK 0x01
#define WEI2_MASK 0x02
#define WEI3_MASK 0x04
#define WEI4_MASK 0x08

// 百分号段码（共阴极）
#define PERCENT_SIGN 0x63

// 全局变量
unsigned char completion_rate = 0;   // 完成率（0-100）
unsigned char receive_buffer[20];    // 串口接收缓冲区
unsigned char receive_index = 0;     // 接收缓冲区索引
unsigned char receive_complete = 0;  // 接收完成标志
unsigned char current_display_pos = 0; // 当前显示的数码管位置
unsigned char play_sound_flag = 0;   // 播放提示音标志

unsigned char NixieTable[]={0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x6F};

//数码管显示子函数
void display_digit(unsigned char Location,Number)
{
	switch(Location)		//位码输出
	{
		case 1:P2_4=1;P2_3=1;P2_2=  1;break;
		case 2:P2_4=1;P2_3=1;P2_2=0;break;
		case 3:P2_4=1;P2_3=0;P2_2=1;break;
		case 4:P2_4=1;P2_3=0;P2_2=0;break;
		case 5:P2_4=0;P2_3=1;P2_2=1;break;
		case 6:P2_4=0;P2_3=1;P2_2=0;break;
		case 7:P2_4=0;P2_3=0;P2_2=1;break;
		case 8:P2_4=0;P2_3=0;P2_2=0;break;
	}
      

void init_serial();
void init_timer();
void display_digit(unsigned char position, unsigned char digit);
void parse_data();
void delay(unsigned int ms);
void play_buzzer_sound();

// 主函数
void main() {
    // 初始化
    init_serial();
    init_timer();
    
    // 设置引脚为输出模式
    DIG_PORT = 0x00;  // 初始状态数码管熄灭（共阴极）
    WEI_PORT = 0xff;  // 初始状态数码管位选关闭
    BUZZER_OFF;       // 初始状态蜂鸣器关闭

    // 主循环
    while (1) {
        // 如果接收到完整数据
        if (receive_complete) {
            parse_data();           // 解析接收到的数据
            receive_complete = 0;   // 重置接收完成标志
            receive_index = 0;      // 重置接收索引
        }
        
        // 如果需要播放提示音
        if (play_sound_flag) {
            play_buzzer_sound();
            play_sound_flag = 0;
        }
    }
}

// 初始化串口通信
void init_serial() {
    SCON = 0x50;  // 串口工作在模式1，允许接收
    TMOD = 0x20;  // 定时器1工作在模式2（自动重装）
    TH1 = 0xfd;   // 波特率9600（晶振11.0592MHz）
    TL1 = 0xfd;
    TR1 = 1;      // 启动定时器1
    ES = 1;       // 允许串口中断
    EA = 1;       // 允许总中断
}

// 初始化定时器0用于数码管动态扫描
void init_timer() {
    TMOD |= 0x01;  // 定时器0工作在模式1
    TH0 = (65536 - 5000) / 256;  // 定时5ms（更快的扫描频率）
    TL0 = (65536 - 5000) % 256;
    ET0 = 1;       // 允许定时器0中断
    TR0 = 1;       // 启动定时器0
}

// 解析接收到的数据
void parse_data() {
    unsigned char i;
    
    // 查找指令类型
    for (i = 0; i < receive_index; i++) {
        // 完成率指令：P后跟百分率值（0-100）
        if (receive_buffer[i] == 'P' && i + 1 < receive_index) {
            completion_rate = receive_buffer[i + 1];
            // 确保完成率在有效范围内
            if (completion_rate > 100) {
                completion_rate = 100;
            }
            // 发送确认信号
            SBUF = 'P';
            while (!TI);
            TI = 0;
            break;
        }
        // 播放声音指令：S
        if (receive_buffer[i] == 'S') {
            play_sound_flag = 1;
            // 发送确认信号
            SBUF = 'S';
            while (!TI);
            TI = 0;
            break;
        }
    }
}

// 延时函数
void delay(unsigned int ms) {
    unsigned int i, j;
    for (i = 0; i < ms; i++) {
        for (j = 0; j < 120; j++);  // 大约1ms的延时（晶振11.0592MHz）
    }
}

// 蜂鸣器播放提示音（模拟end.mp3效果）
void play_buzzer_sound() {
    unsigned int i, j;
    
    // 播放一段简单的旋律
    for (i = 0; i < 3; i++) {
        // 高音
        for (j = 0; j < 200; j++) {
            BUZZER_TOGGLE;
            delay(1);
        }
        
        // 低音
        for (j = 0; j < 200; j++) {
            BUZZER_TOGGLE;
            delay(2);
        }
    }
    
    BUZZER_OFF;  // 关闭蜂鸣器
}

// 串口中断服务函数
void serial_isr() interrupt 4 {
    if (RI) {
        RI = 0;  // 清除接收中断标志
        
        // 读取接收到的数据
        receive_buffer[receive_index] = SBUF;
        
        // 检查是否接收到换行符，表示数据帧结束
        if (receive_buffer[receive_index] == '\n' || receive_index >= 19) {
            receive_complete = 1;
        } else {
            receive_index++;
        }
    }
    
    if (TI) {
        TI = 0;  // 清除发送中断标志
    }
}

// 定时器0中断服务函数（用于数码管动态扫描）
void timer0_isr() interrupt 1 {
    unsigned char hundreds, tens, units;
    
    TH0 = (65536 - 5000) / 256;  // 重新加载初值
    TL0 = (65536 - 5000) % 256;
    
    // 循环显示不同的位置
    current_display_pos++;
    if (current_display_pos > 4) {
        current_display_pos = 1;
    }
    
    // 分解完成率为百位、十位和个位
    hundreds = completion_rate / 100;
    tens = (completion_rate % 100) / 10;
    units = completion_rate % 10;
    
    // 根据当前位置显示相应的数字
    switch (current_display_pos) {
        case 1:
            if (hundreds > 0) {
                display_digit(1, hundreds);  // 显示百位
            } else {
                // 不显示前导零，直接关闭显示
                WEI_PORT = 0xff;
                DIG_PORT = 0x00;
            }
            break;
        case 2:
            if (hundreds > 0 || tens > 0) {
                display_digit(2, tens);  // 显示十位
            } else {
                // 不显示前导零，直接关闭显示
                WEI_PORT = 0xff;
                DIG_PORT = 0x00;
            }
            break;
        case 3:
            display_digit(3, units);  // 显示个位
            break;
        case 4:
            display_digit(4, 10);  // 显示百分号
            break;
    }
}