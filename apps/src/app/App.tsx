import {
  Route,
  BrowserRouter as Router,
  Routes,
} from 'react-router-dom';
import NavBar from '../components/NavBar';
import GroceryListPage from '../pages/GroceryListPage';
import HomePage from '../pages/HomePage';
import MealPlanPage from '../pages/MealPlanPage';
import NewRecipePage from '../pages/NewRecipePage';
import RecipesPage from '../pages/RecipesPage';
import { Theme } from '../theme/Theme';

export default function App() {
  return (
    <Theme>
      <Router>
        <NavBar />
        <Routes>
          <Route path="home" element={<HomePage />} />
          <Route path="new-recipe" element={<NewRecipePage />} />
          <Route path="recipes" element={<RecipesPage />} />
          <Route path="meal-plan" element={<MealPlanPage />} />
          <Route path="grocery-list" element={<GroceryListPage />} />
        </Routes>
      </Router>
    </Theme>
  );
};
