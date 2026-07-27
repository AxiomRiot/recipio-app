import { useState } from 'react';
import styled from 'styled-components';

const NavBarDiv = styled.div`
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
  min-height: 10vh;
  width: full;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  background: ${({ theme }) => theme.colors.kitchenGreen};
`;

const BrandingTitle = styled.h1`
  font-family: ${({ theme }) => theme.typography.fonts.display};
  color: ${({ theme }) => theme.colors.creamWhite};
  font-size: 1.5em;
  font-weight: 600;

  margin-left: 32px;
`;

const NavBarLinksDiv = styled.div`
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
`;

const AddRecipeDiv = styled.div`
  display: flex;
  flex-direction: row;
  align-items: flex-start;
`;

const NavButton = styled.button<{ isActive: boolean }>`
  background: none;
  border: none;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  color:'#E9E7E2';
  opacity: ${props => props.isActive ? 1 : 0.75};
  border-bottom: ${({ theme, isActive }) => isActive ? `2px solid ${theme.colors.highlightYellow}` : 'none'};
`;

const NewRecipeButton = styled.button`
  padding: 9px 14px;
  margin-right: 32px;

  background-color: ${({ theme }) => theme.colors.urgentRed};
  color:'#E9E7E2';

  border: none;
  border-radius: 3px;

  cursor: pointer;

  font-family: ${({ theme }) => theme.typography.fonts.display};
  text-transform: uppercase;
  font-size: 12.5px;
  letter-spacing: 0.06em;
`;

const NAVBAR_DATA = [
  { text: 'This Week', path: 'home' },
  { text: 'Recipe Box', path: 'recipes' },
  { text: 'Meal Plan', path: 'meal-plan' },
  { text: 'Grocery List', path: 'grocery-list' },
];

export default function NavBar() {
  const [activeButton, setActiveButton] = useState('home');

  function handleOnClick(path: string) {
    setActiveButton(path);
  }

  return (
    <NavBarDiv>
      <BrandingTitle>Recipio</BrandingTitle>
      <NavBarLinksDiv>
        {NAVBAR_DATA.map((item, index) => (
          <NavButton key={index} onClick={() => handleOnClick(item.path)} isActive={activeButton === item.path}>{item.text}</NavButton>
        ))}
      </NavBarLinksDiv>
      <AddRecipeDiv>
        <NewRecipeButton>New Recipe</NewRecipeButton>
      </AddRecipeDiv>
    </NavBarDiv>
  );
};
