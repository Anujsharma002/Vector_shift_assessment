// frontend/src/integrations/hubspot.js

import { useState, useEffect } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import axios from 'axios';

export const HubSpotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    // Function to open OAuth in a new window
    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);

            // Request the HubSpot authorization URL
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/authorize`, formData);
            const authURL = response.data;

            // Open the OAuth window
            const newWindow = window.open(authURL, 'HubSpot Authorization', 'width=600,height=600');

            // Polling to detect when the window closes
            const pollTimer = setInterval(() => {
                if (!newWindow || newWindow.closed) {
                    clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200);
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail || 'Error connecting to HubSpot');
        }
    };

    // Function to handle logic when the OAuth window closes
    const handleWindowClosed = async () => {
        try {
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);

            const response = await axios.post(`http://localhost:8000/integrations/hubspot/credentials`, formData);
            const credentials = response.data;

            if (credentials) {
                setIntegrationParams(prev => ({
                    ...prev,
                    credentials: credentials,
                    type: 'HubSpot'
                }));
                setIsConnected(true);
            }
            setIsConnecting(false);
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail || 'Failed to fetch HubSpot credentials');
        }
    };

    useEffect(() => {
        setIsConnected(!!integrationParams?.credentials);
    }, []);

    return (
        <Box sx={{ mt: 2 }}>
            HubSpot Parameters
            <Box display='flex' alignItems='center' justifyContent='center' sx={{ mt: 2 }}>
                <Button 
                    variant='contained'
                    onClick={isConnected ? () => {} : handleConnectClick}
                    color={isConnected ? 'success' : 'primary'}
                    disabled={isConnecting}
                    style={{
                        pointerEvents: isConnected ? 'none' : 'auto',
                        cursor: isConnected ? 'default' : 'pointer',
                        opacity: isConnected ? 1 : undefined
                    }}
                >
                    {isConnected 
                        ? 'HubSpot Connected' 
                        : isConnecting 
                        ? <CircularProgress size={20} /> 
                        : 'Connect to HubSpot'}
                </Button>
            </Box>
        </Box>
    );
};
