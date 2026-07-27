import styled from 'styled-components';
import NavBar from '../components/NavBar';
import { Theme } from '../theme/Theme';

const AppDiv = styled.div`
  margin: 0;
  padding: 0;
  background: red;
`;

export default function App() {
  return (
    <Theme>
      <AppDiv>
        <NavBar />
      </AppDiv>
    </Theme>
  );
};
