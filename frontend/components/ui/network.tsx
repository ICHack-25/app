'use client';

import React from 'react';
import { GraphCanvas, darkTheme, GraphEdge } from 'reagraph';
import { NetworkProps, DataObject, convertToNodes, Node } from '@/components/dataobject';

export const Network: React.FC<NetworkProps> = ({ data }) => {
    // Define nodes and edges based on the data you pass in


    const nodes = convertToNodes(data);


    const edges : GraphEdge[] = [];

    // Handle node click by opening the node's URL
    const handleNodeClick = (node: any) => {
        const nodeData = node.data;
        if (nodeData && nodeData.url) {
            window.open(nodeData.url, '_blank');  // Open URL in a new tab
        }
    };

    return (
        <div style={{
            width: '600px',  // Set fixed width
            height: '400px', // Set fixed height
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
