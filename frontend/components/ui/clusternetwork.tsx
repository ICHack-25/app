'use client';

import React from 'react';
import { ThreeEvent } from '@react-three/fiber';
import { GraphCanvas, darkTheme, InternalGraphNode, GraphNode } from 'reagraph';
import { NetworkProps, DataObject, convertToNodes, Node } from '@/components/dataobject';
import axios from 'axios';

const nodes = [
    { id: 'n-1', label: 'Node 1', data: { type: 'A', url: 'https://example.com/1' } },
    { id: 'n-2', label: 'Node 2', data: { type: 'B', url: 'https://example.com/2' } },
    { id: 'n-3', label: 'Node 3', data: { type: 'A', url: 'https://example.com/3' } },
    { id: 'n-4', label: 'Node 4', data: { type: 'B', url: 'https://example.com/4' } },
    { id: 'n-5', label: 'Node 5', data: { type: 'A', url: 'https://example.com/5' } },
    { id: 'n-6', label: 'Node 6', data: { type: 'B', url: 'https://example.com/6' } }
];

export const ClusterNetwork = ({data}  : NetworkProps) => {

    const nodes = convertToNodes(data);
    const edges : GraphNode[] = [];

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
        <>
            <div
                style={{
                    width: '60vw',
                    height: '500px',
                    position: 'relative',
                    border: '1px solid #EA5925',
                    overflow: 'hidden',
                    borderRadius: '10px',
                }}
            >
                <GraphCanvas
                    theme={darkTheme}
                    nodes={nodes}
                    draggable
                    edges={[{
                        source: 'n-6',
                        target: 'n-1',
                        id: 'n-6-n-1',
                        label: 'n-6-n-1'
                    }]}
                    clusterAttribute="type"
                    constrainDragging={false}
                    onNodeClick={handleNodeClick}
                />
            </div>
            <div
                style={{
                    zIndex: 9,
                    position: 'absolute',
                    top: 15,
                    right: 15
                }}
            >
            </div>
        </>
    );
};
