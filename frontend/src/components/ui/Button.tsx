import { ButtonHTMLAttributes, ReactNode } from 'react';
import { Spinner } from './Spinner';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    isLoading?: boolean;
    children: ReactNode;
}

export function Button({ isLoading, children, ...props }: ButtonProps) {
    return (
        <button
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={isLoading}
            {...props}
        >
            {isLoading ? (
                <>
                    <Spinner className="w-5 h-5 mr-3" />
                    Processing...
                </>
            ) : children}
        </button>
    );
}
