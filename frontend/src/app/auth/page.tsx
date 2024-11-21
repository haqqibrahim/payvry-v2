'use client';

import { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { SignupForm } from '@/components/auth/SignupForm';

export default function AuthPage() {
    const [activeTab, setActiveTab] = useState('login');

    return (
        <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-md w-full space-y-8">
                {/* Logo and Title */}
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                        Welcome to Payvry
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Secure P2P Payment Platform
                    </p>
                </div>

                {/* Auth Tabs */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <div className="flex border-b mb-4">
                        <button
                            onClick={() => setActiveTab('login')}
                            className={`flex-1 py-2 text-center font-medium ${activeTab === 'login' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
                        >
                            Login
                        </button>
                        <button
                            onClick={() => setActiveTab('signup')}
                            className={`flex-1 py-2 text-center font-medium ${activeTab === 'signup' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Conditional Rendering of Forms */}
                    {activeTab === 'login' ? <LoginForm /> : <SignupForm />}
                </div>
            </div>
        </div>
    );
}
