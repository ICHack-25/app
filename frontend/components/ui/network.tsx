'use client';

import React from 'react';
import { GraphCanvas, darkTheme, GraphEdge } from 'reagraph';
import { NetworkProps, DataObject, convertToNodes, Node } from '@/components/dataobject';
import axios from 'axios';

export const Network: React.FC<NetworkProps> = ({ data }) => {
    // Define nodes and edges based on the data you pass in


    const nodes = convertToNodes(data);


    const edges : GraphEdge[] = [];

    const handleNodeClick = async (node : any) => {
        try {
            const resourceName = node.data.name;
            // Make sure to include the API key in headers
            const response = await axios.get(`http://localhost:5000/download/${resourceName}`, {
                headers: {
                    'X-API-Key': 'YOUR_API_KEY',  // Replace with your actual key
                },
                responseType: 'blob', // Important to get raw binary data
            });

            // Create a Blob from the response data
            const fileBlob = new Blob([response.data], {
                type: response.headers['content-type'] || 'application/octet-stream'
            });

            // Generate a temporary object URL for the blob
            const fileBlobUrl = URL.createObjectURL(fileBlob);

            // If it's an image, you can set the URL as the `src` of an <img> element
            // or if you just want to force a download, you can simulate a link click:

            // Option 1: Display in a new browser tab (good for PDFs, images, etc.)
            window.open(fileBlobUrl, '_blank');

            // Option 2: Force a file download
            // const link = document.createElement('a');
            // link.href = fileBlobUrl;
            // link.setAttribute('download', filename);
            // document.body.appendChild(link);
            // link.click();
            // document.body.removeChild(link);

            // Or update state to use in your component, e.g. an <img>:
            // setFileUrl(fileBlobUrl);
        } catch (error) {
            console.error('File download error:', error);
        }
    };

    return (
        <div style={{
            width: '100%',  // Set fixed width
            height: '300px', // Set fixed height
            position: 'relative',
            border: '1px solid #EA5925', // Optional: for visual boundary
            overflow: 'hidden', // Optional: to prevent overflow
        }}>
            <GraphCanvas
                theme={darkTheme}
                nodes={nodes}
                edges={edges}
                onNodeClick={handleNodeClick}  // Attach the correct handler to onNodeClick
            />
        </div>
    );
};
