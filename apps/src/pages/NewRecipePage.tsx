import styled from 'styled-components';
import Ticket from '../components/Ticket';

const PageDiv = styled.div`
  margin: 0 auto;
  padding: 34px 24px 90px;
  box-sizing: border-box;
  min-height: 100%;
`;

const TicketDiv = styled.div`
  max-width: 760px;
  margin: 0 auto;
  padding: 34px 24px 90px;
`;

const TicketEyebrow = styled.p`
  display: block;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  unicode-bidi: isolate;

  font-family: '${({ theme }) => theme.typography.fonts.data};';
  color: ${({ theme }) => theme.colors.ink};
  font-style: normal;
  font-weight: 400;
  font-display: swap;
`;

const PageTitle = styled.h1`
  display: block;
  font-size: 2em;
  margin-block-start: 0.67em;
  margin-block-end: 0.67em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  font-weight: bold;
  unicode-bidi: isolate;

  color: ${({ theme }) => theme.colors.ink};
  font-family: '${({ theme }) => theme.typography.fonts.data};';
  text-transform: uppercase;
`;

export default function NewRecipePage() {
  return (
    <PageDiv>
      <Ticket>
        <TicketDiv>
          <TicketEyebrow>New Ticket</TicketEyebrow>
          <PageTitle>Add A Recipe</PageTitle>
        </TicketDiv>
      </Ticket>
    </PageDiv>
  );
};
