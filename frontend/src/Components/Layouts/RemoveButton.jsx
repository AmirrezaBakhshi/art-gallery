

//  COMMMENDTED

import "../../assets/CSS/button.css";

import { useTranslation } from 'react-i18next';

function RemoveButton(params) {

  const {t} = useTranslation(['gallaryinfo']);

  const handleClick = () => {
    params.stateChanger(null);
  };

  return (
    <button className="remove-button" onClick={handleClick}>
      {t('remove')}
    </button>
  );
}

export default RemoveButton;