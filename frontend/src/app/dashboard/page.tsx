'use client';

import React, { useEffect, useState } from 'react';

const Dashboard = () => {
    const [phoneNumber, setPhoneNumber] = useState<string | null>(null);

    useEffect(() => {
        // Access localStorage only in the browser
        const storedPhoneNumber = localStorage.getItem('phoneNumber');
        setPhoneNumber(storedPhoneNumber);
    }, []);

    return (
        <div className="bg-white min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 text-center">
                <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                    Welcome to Your Dashboard
                </h2>
                <p className="mt-4 text-lg text-gray-600">
                    Your registered phone number is: <strong>{phoneNumber}</strong>
                </p>
                <div className="mt-8">
                    <a href="https://wa.me/2347049908187?text=Start" 
                       target="_blank"
                       className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-full shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                        Chat with Payvry AI
                    </a>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;