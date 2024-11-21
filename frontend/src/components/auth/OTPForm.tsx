import { useState } from 'react';

interface OTPFormProps {
    onVerified: () => void;
    onResend: () => void;
    whatsapp: string;
}

export function OTPForm({ onVerified, onResend, whatsapp }: OTPFormProps) {
    const [otp, setOtp] = useState<string[]>(Array(6).fill(''));
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (index: number, value: string) => {
        const newOtp = [...otp];
        newOtp[index] = value;

        if (value.length === 1 && index < otp.length - 1) {
            const nextInput = document.querySelector(`input[data-index="${index + 1}"]`) as HTMLInputElement;
            nextInput?.focus();
        }

        setOtp(newOtp);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        const otpCode = otp.join('');
        
        console.log("Submitting OTP:", otpCode, "for WhatsApp:", whatsapp);

        // Commenting out the OTP verification logic
        /*
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    whatsapp_number: whatsapp,
                    otp_code: otpCode,
                }),
            });

            const data = await response.json();
            console.log("Response:", data);
            if (response.ok) {
                alert('OTP verified successfully!');
                onVerified();
            } else {
                alert(data.detail || 'OTP verification failed');
            }
        } catch (error) {
            console.error('OTP verification error:', error);
            alert('An error occurred during OTP verification');
        } finally {
            setIsLoading(false);
        }
        */
    };

    return (
        <div className="space-y-4" id="otpForm">
            <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">Verify OTP</h3>
                <p className="mt-1 text-sm text-gray-500">
                    We've sent a verification code to your phone
                </p>
            </div>
            <form onSubmit={handleSubmit} className="flex justify-center space-x-2">
                {otp.map((digit, index) => (
                    <input
                        key={index}
                        type="text"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleChange(index, e.target.value)}
                        data-index={index}
                        className="w-12 h-12 text-center border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-black"
                    />
                ))}
                <button
                    type="submit"
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    disabled={isLoading}
                >
                    <span className="inline-flex items-center">
                        {isLoading && (
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        )}
                        Verify OTP
                    </span>
                </button>
            </form>
            <button
                onClick={onResend}
                className="w-full flex justify-center py-2 px-4 text-sm font-medium text-blue-600 hover:text-blue-500"
            >
                Resend OTP
            </button>
        </div>
    );
}
