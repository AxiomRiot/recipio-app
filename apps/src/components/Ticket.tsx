import type { ReactNode } from 'react';
import styled from 'styled-components';

interface TicketProps {
  children: ReactNode;
}

const TicketDiv = styled.div`
  background: #E9E7E2;
  padding: 26px 28px;
  margin-bottom: 24px;
  clip-path: polygon(0% 100%, 0% var(--tear), 7% var(--tear-peak), 14% var(--tear), 21% var(--tear-peak), 29% var(--tear), 36% var(--tear-peak), 43% var(--tear), 50% var(--tear-peak), 57% var(--tear), 64% var(--tear-peak), 71% var(--tear), 79% var(--tear-peak), 86% var(--tear), 93% var(--tear-peak), 100% var(--tear), 100% 100%);
`;

export default function Ticket({ children }: TicketProps) {
  return (
    <TicketDiv style={{ '--tear-peak': '4px', '--tear': '14px' }}>
      {children}
    </TicketDiv>
  );
}
