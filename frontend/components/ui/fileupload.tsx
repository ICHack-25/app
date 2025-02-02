'use client';

import React, { useState, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { FiUpload } from "react-icons/fi";
import {ArrowRight} from "lucide-react";
import {Button} from "@/components/ui/button"; // You can use any icon library
import { FaCog } from "react-icons/fa";

export function InputFile() {
    const [file, setFile] = useState<File | null>(null);

    // Handle file selection or drop
    const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files ? e.target.files[0] : null;
        if (selectedFile) {
            setFile(selectedFile);
        }
    }, []);

    // Handle drag and drop
    const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
        }
    }, []);

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
    };

    return (
        <div className="grid place-items-center lg:max-w-screen-xl gap-8 mx-auto py-20 md:py-32">
            <div className="text-center space-y-8">

                    <h2 className="text-3xl md:text-4xl text-center font-bold mb-4">Upload a File</h2>
                    <label
                        htmlFor="picture" // The label will be used to open the file input dialog
                        className="border-2 border-[#EA5925] p-4 rounded-lg cursor-pointer hover:bg-[#EA5925] hover:text-white transition-all duration-300 ease-in-out flex flex-col items-center justify-center"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                    >
                        <Input
                            id="picture"
                            type="file"
                            onChange={handleFileChange}
                            className="hidden" // Hidden file input, but still functional
                        />
                        <div className="flex flex-col items-center justify-center">
                            {!file ? (
                                <>
                                    <FiUpload className="text-white mb-2" size={40} />
                                    <span className="text-white">Drag and drop or click to select a file</span>
                                </>
                            ) : (
                                <span className="textwhite">File: {file.name}</span> // Display the file name
                            )}
                        </div>
                    </label>

                    {/* Conditionally render the 'Analyse information' button after file upload */}
                    {file && (
                        <div className="space-y-4 md:space-y-0 md:space-x-4">
                            <Button className="w-full font-bold group/arrow">
                                Analyse Information <FaCog className="ml-2"/>
                            </Button>
                        </div>

                    )}
                </div>

        </div>


    );
}
